#!/usr/bin/env python3
# Local instruct-model chat with logging, slash-commands, colors, multiline input
# Autocomplete shows only when typing a slash-command, or when pressing Tab.
# Requires: transformers, torch, rich, prompt_toolkit

from dataclasses import dataclass
from pathlib import Path
import re
import random
import threading
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from typing import List, Optional
import time

from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

# prompt_toolkit (optional but recommended)
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter, DynamicCompleter, Completer

# key bindings for the console shortcuts
from key_map import KeyMap
from console_app import ConsoleApp

# ---------------- Chat plumbing ----------------

@dataclass
class Turn:
    role: str  # "user" | "assistant"
    content: str

def apply_chat_template_if_available(tok, system_msg: str, turns: List[Turn]) -> Optional[str]:
    if not hasattr(tok, "apply_chat_template"):
        return None
    msgs = []
    if system_msg:
        msgs.append({"role": "system", "content": system_msg})
    for t in turns:
        msgs.append({"role": t.role, "content": t.content})
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    except Exception:
        return None

def build_manual_prompt(system_msg: str, turns: List[Turn]) -> str:
    parts = []
    if system_msg:
        parts.append(system_msg.strip())
    for t in turns:
        if t.role == "user":
            parts.append(f"\nUser: {t.content.strip()}\nAssistant:")
        else:
            parts.append(f" {t.content.strip()}\n")
    if not turns or turns[-1].role != "assistant":
        parts.append("\nAssistant:")
    return "".join(parts)

def build_input_text(tok, system_msg: str, turns: List[Turn]) -> str:
    t = apply_chat_template_if_available(tok, system_msg, turns)
    return t if t is not None else build_manual_prompt(system_msg, turns)

def pick_dtype(arg: str, device: str):
    if arg != "auto":
        return {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}[arg]
    return torch.float16 if device == "mps" else torch.float32

def adaptive_max_new(input_tokens: int, user_max: Optional[int]) -> int:
    if user_max is not None:
        return user_max
    return max(128, min(512, input_tokens * 2))

def set_seed_everywhere(seed: int):
    if seed and seed > 0:
        torch.manual_seed(seed)
        try:
            import numpy as np
            random.seed(seed); np.random.seed(seed)
        except Exception:
            pass

# ---------------- Logging ----------------

def safe_model_name(mid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", mid)

def ensure_log_path(model_id: str) -> Path:
    base = Path.home() / ".local_chat_logs" / safe_model_name(model_id)
    base.mkdir(parents=True, exist_ok=True)
    return base

def new_log_file(model_id: str) -> Path:
    base = ensure_log_path(model_id)
    ts = time.strftime("%Y%m%d-%H%M%S")
    return base / f"{ts}.md"

def append_log(log_path: Path, text: str):
    log_path.write_text((log_path.read_text() if log_path.exists() else "") + text, encoding="utf-8")

def init_log(log_path: Path, model_id: str, system_msg: str, args):
    header = f"""# Local Chat Log
- **Model**: `{model_id}`
- **Started**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **Device**: `{args.device or ('mps' if torch.backends.mps.is_available() else 'cpu')}`
- **Params**: temperature={args.temperature}, top_p={args.top_p}, top_k={args.top_k}, rep_penalty={args.rep_penalty}, greedy={args.greedy}, max_new={args.max_new or 'adaptive'}

## System
> {system_msg}

---
"""
    append_log(log_path, header)

def log_turn(log_path: Path, role: str, content: str):
    block = f"\n### {role.title()}\n\n{content}\n"
    append_log(log_path, block)

def log_divider(log_path: Path, label: str = "Session divider"):
    append_log(log_path, f"\n---\n*{label} @ {time.strftime('%Y-%m-%d %H:%M:%S')}*\n---\n")

# ---------------- Generation ----------------

def generate_once(model, tok, device: str, prompt_text: str,
                  max_new: Optional[int], temperature: float, top_p: float, top_k: int,
                  rep_penalty: float, greedy: bool, stream: bool) -> str:
    inputs = tok(prompt_text, return_tensors="pt").to(device)
    computed_max = adaptive_max_new(inputs["input_ids"].shape[1], max_new)
    gen_kwargs = dict(
        max_new_tokens=computed_max,
        eos_token_id=tok.eos_token_id,
        pad_token_id=tok.eos_token_id,
        repetition_penalty=rep_penalty,
    )
    if greedy:
        gen_kwargs.update(dict(do_sample=False))
    else:
        gen_kwargs.update(dict(do_sample=True, temperature=temperature, top_p=top_p))
        if top_k and top_k > 0:
            gen_kwargs["top_k"] = top_k

    if stream:
        streamer = TextIteratorStreamer(tok, skip_special_tokens=True, skip_prompt=True)
        gen_kwargs["streamer"] = streamer

        def run():
            with torch.no_grad():
                model.generate(**inputs, **gen_kwargs)

        t = threading.Thread(target=run, daemon=True)
        t.start()
        out_chunks: List[str] = []
        for piece in streamer:
            console.print(piece, end="")
            out_chunks.append(piece)
        console.print()
        return "".join(out_chunks)
    else:
        with torch.no_grad():
            out = model.generate(**inputs, **gen_kwargs)
        return tok.decode(out[0], skip_special_tokens=True)

# ---------------- Dice roller ----------------

_DICE_RE = re.compile(
    r"""^\s*(?P<count>\d+)?d(?P<sides>\d+)(?P<keep>(k|kl|kh)\d+)?(?P<mod>[+-]\d+)?\s*$""",
    re.IGNORECASE | re.VERBOSE,
)

def parse_dice(expr: str):
    m = _DICE_RE.match(expr)
    if not m:
        raise ValueError("Dice syntax: [N]dM[kl/khN][+/-X]  e.g., 1d20+5, 2d20k1, 2d20kl1")
    count = int(m.group("count")) if m.group("count") else 1
    sides = int(m.group("sides"))
    keep = m.group("keep")
    mod = int(m.group("mod")) if m.group("mod") else 0
    keep_mode = None; keep_n = None
    if keep:
        keep = keep.lower()
        if keep.startswith("kh"): keep_mode, keep_n = "kh", int(keep[2:])
        elif keep.startswith("kl"): keep_mode, keep_n = "kl", int(keep[2:])
        elif keep.startswith("k"):  keep_mode, keep_n = "kh", int(keep[1:])
    if keep_n is not None and (keep_n <= 0 or keep_n > count):
        raise ValueError("Keep N must be between 1 and the number of dice.")
    if count <= 0 or sides <= 1:
        raise ValueError("Use at least 1 die and sides >= 2.")
    return dict(count=count, sides=sides, keep_mode=keep_mode, keep_n=keep_n, mod=mod)

def roll_dice(spec: dict):
    count, sides = spec["count"], spec["sides"]
    keep_mode, keep_n, mod = spec["keep_mode"], spec["keep_n"], spec["mod"]
    rolls = [random.randint(1, sides) for _ in range(count)]
    kept = rolls[:]; note = ""
    if keep_mode and keep_n is not None:
        if keep_mode == "kh":
            kept = sorted(rolls, reverse=True)[:keep_n]; note = f" (keep highest {keep_n})"
        else:
            kept = sorted(rolls)[:keep_n]; note = f" (keep lowest {keep_n})"
    subtotal = sum(kept); total = subtotal + mod
    parts = [f"Roll: {count}d{sides}{note}", f"All: {rolls}"]
    if kept != rolls: parts.append(f"Kept: {kept}")
    if mod: parts.append(f"Modifier: {mod:+d}")
    parts.append(f"Total: {total}")
    return total, rolls, kept, " | ".join(parts)

def summarize_recent(model, tok, turns: List[Turn], k: int = 2) -> str:
    """
    Deterministic, terse, bullet-only summary of the last k turns.
    Never includes the main storyteller system prompt.
    """
    # print(f"summarize_recent: tok: {tok}, k: {k}")
    k = max(1, k)
    recent = turns[-k:] if k <= len(turns) else turns[:]

    # Build a *separate* summarizer instruction (no storyteller persona)
    summ_sys = (
        "You are a neutral meeting scribe.\n"
        "Task: Summarize the recent exchange in 1–3 very short bullets.\n"
        "Rules: Only output Markdown bullets starting with '- '. "
        "No questions, no suggestions, no choices, no headings."
    )

    # Compact context block
    ctx = "\n".join(f"{t.role.upper()}: {t.content.strip()}" for t in recent)
    user_msg = f"Summarize this:\n\n[CONTEXT]\n{ctx}\n[/CONTEXT]\n\nReturn only bullets."

    # Build messages just for the summarizer
    msgs = [{"role": "system", "content": summ_sys}, {"role": "user", "content": user_msg}]

    # Prefer chat template; never add your main system prompt here
    try:
        if hasattr(tok, "apply_chat_template"):
            prompt_text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        else:
            prompt_text = summ_sys + "\n\nUser: " + user_msg + "\nAssistant:"
    except Exception:
        prompt_text = summ_sys + "\n\nUser: " + user_msg + "\nAssistant:"

    inputs = tok(prompt_text, return_tensors="pt").to(model.device)

    out = model.generate(
        **inputs,
        do_sample=False,            # <- deterministic
        temperature=0.0,
        top_p=1.0,
        max_new_tokens=96,
        no_repeat_ngram_size=3,
        pad_token_id=tok.eos_token_id,
        eos_token_id=tok.eos_token_id,
    )

    text = tok.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True).strip()

    # Post-filter: keep only bullet lines; trim anything else if model drifts
    lines = [ln.rstrip() for ln in text.splitlines()]
    bullets = [ln for ln in lines if ln.lstrip().startswith("- ")]
    if bullets:
        return "\n".join(bullets[:3]).strip()
    # Fallback: first sentence as a single bullet
    return "- " + (text.split("\n\n")[0].split(". ")[0].strip().rstrip(".") + ".")

# ---------------- Slash commands ----------------

HELP_TEXT = """\
**Slash commands**
/help                    Show this help
/save                    Save a divider in the log file now
/clear                   Clear chat history (keeps same log file and adds divider)
/system <text>           Set/replace the system prompt
/genre <style>           Switch style (e.g., romcom, noir, sci-fi)
/storyteller             Set Storyteller persona
/dm                      Set Dungeon Master persona
/temp <float>            Set temperature
/top_p <float>           Set top_p
/top_k <int>             Set top_k
/rep <float>             Set repetition penalty
/greedy on|off           Toggle greedy decoding (on = no sampling)
/max <int>               Set max_new_tokens (omit for adaptive)
/seed <int>              Set RNG seed (0 = random)
/model <id>              Switch model (reloads)
/roll <expr>             Roll dice: d20, 1d20+5, 2d20k1, 2d20kl1
/show                    Show current settings
/quit                    Exit
/sum                     Summarize last N interactions
/philosopher             Philosopher mode
"""

def show_settings(args, system_msg: str, model_id: str, log_path: Path):
    table = Text()
    table.append(f"Model: {model_id}\n")
    table.append(f"System: {system_msg}\n")
    table.append(f"Device: {args.device or ('mps' if torch.backends.mps.is_available() else 'cpu')}\n")
    table.append(f"temperature={args.temperature}, top_p={args.top_p}, top_k={args.top_k}, "
                 f"rep_penalty={args.rep_penalty}, greedy={args.greedy}, max_new={args.max_new or 'adaptive'}\n")
    table.append(f"Log file: {str(log_path)}\n")
    console.print(Panel(table, title="Current settings", expand=False))

def parse_command(s: str):
    parts = s.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    return cmd, arg

# ---------------- Entrypoint ----------------

def main():
    console = ConsoleApp()
    args = console.args
    model = args.model
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(model, dtype=dtype, device_map={"": device})

    log_path = new_log_file(args.model)
    init_log(log_path, args.model, args.system, args)

    console.print("\n[bold]🗨️  Interactive chat mode.[/bold]  Enter to send; Shift+Enter for newline.  Type /help for commands.  Empty line or /quit to exit.\n")

    history: List[Turn] = []

    # ---------- Autocomplete only on "/" ----------
    slash_words = ["/help","/save","/clear","/system","/genre","/storyteller","/dm",
                   "/temp","/top_p","/top_k","/rep","/greedy","/max","/seed",
                   "/model","/roll","/show","/quit","/exit","/sum","/philosopher"]

    base_completer = WordCompleter(slash_words, ignore_case=True)

    class SlashOnlyCompleter(Completer):
        def get_completions(self, document, complete_event):
            text = document.current_line_before_cursor
            if text.lstrip().startswith("/"):
                yield from base_completer.get_completions(document, complete_event)
            # else: no suggestions

    kb = KeyMap.kb
    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        completer=SlashOnlyCompleter(),
        complete_while_typing=True,   # safe: only active when line startswith("/")
        multiline=True,
        prompt_continuation="… ",
        key_bindings=kb,
    )

    def read_user() -> Optional[str]:
        try:
            return session.prompt("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            return None

    while True:
        user = read_user()
        if user is None or user == "":
            console.print("bye!")
            break

        if user.startswith("/"):
            cmd, arg = parse_command(user)
            if cmd in ("/quit", "/exit"):
                console.print("bye!"); break
            elif cmd == "/help":
                console.print(Markdown(HELP_TEXT))
            elif cmd == "/save":
                log_divider(log_path, "Manual save"); console.print(f"[green]Saved divider to[/green] {log_path}")
            elif cmd == "/clear":
                history.clear(); log_divider(log_path, "History cleared"); console.print("[yellow]History cleared.[/yellow]")
            elif cmd == "/system":
                args.system = arg or args.system
                log_divider(log_path, "System prompt changed")
                console.print(Panel(Markdown(f"**System set to:**\n\n> {args.system}"), title="System"))
            elif cmd == "/genre":
                if not arg.strip():
                    console.print("[yellow]Usage:[/yellow] /genre <style>")
                else:
                    args.system = f"You are telling a story in the style of a {arg.strip()}."
                    log_divider(log_path, f"Genre -> {arg.strip()}")
                    console.print(f"[green]Storyteller style changed to {arg.strip()}.[/green]")
            elif cmd == "/storyteller":
                args.system = ("You are a creative narrator who continues and embellishes user ideas with style and humor. "
                               "Advance plot, deepen characters, and end with a natural beat.")
                console.print("[green]Switched to Storyteller mode.[/green]")
            elif cmd == "/dm":
                args.system = ("You are a Dungeon Master guiding a player through a fantasy adventure. "
                               "Describe environments, ask for actions, and use dice outcomes when relevant.")
                console.print("[green]Switched to Dungeon Master mode.[/green]")
            elif cmd == "/temp":
                try: args.temperature = float(arg); console.print(f"[green]temperature=[/green]{args.temperature}")
                except: console.print("[red]Usage:[/red] /temp 0.7")
            elif cmd == "/top_p":
                try: args.top_p = float(arg); console.print(f"[green]top_p=[/green]{args.top_p}")
                except: console.print("[red]Usage:[/red] /top_p 0.9")
            elif cmd == "/top_k":
                try: args.top_k = int(arg); console.print(f"[green]top_k=[/green]{args.top_k}")
                except: console.print("[red]Usage:[/red] /top_k 40")
            elif cmd == "/rep":
                try: args.rep_penalty = float(arg); console.print(f"[green]repetition_penalty=[/green]{args.rep_penalty}")
                except: console.print("[red]Usage:[/red] /rep 1.05")
            elif cmd == "/greedy":
                args.greedy = arg.lower() in ("on","true","1")
                console.print(f"[green]greedy=[/green]{args.greedy}")
            elif cmd == "/max":
                if arg.strip() == "": args.max_new = None
                else:
                    try: args.max_new = int(arg)
                    except: console.print("[red]Usage:[/red] /max 256"); continue
                console.print(f"[green]max_new=[/green]{args.max_new or 'adaptive'}")
            elif cmd == "/seed":
                try: args.seed = int(arg); set_seed_everywhere(args.seed); console.print(f"[green]seed=[/green]{args.seed}")
                except: console.print("[red]Usage:[/red] /seed 1234")
            elif cmd == "/model":
                new_id = arg.strip()
                if not new_id: console.print("[red]Usage:[/red] /model repo_or_path")
                else:
                    console.print(f"[yellow]Loading model:[/yellow] {new_id} …")
                    tok = AutoTokenizer.from_pretrained(new_id)
                    model = AutoModelForCausalLM.from_pretrained(new_id, dtype=dtype, device_map={"": device})
                    log_path = new_log_file(new_id); init_log(log_path, new_id, args.system, args)
                    console.print(f"[green]Switched model. New log:[/green] {log_path}")
                    args.model = new_id; history.clear()
            elif cmd == "/roll":
                expr = arg.strip()
                if not expr:
                    console.print("[red]Usage:[/red] /roll 1d20+5  (supports k/kh/kl, e.g., 2d20k1)")
                else:
                    try:
                        spec = parse_dice(expr)
                        total, rolls, kept, breakdown = roll_dice(spec)
                        console.print(Panel(f"[bold]🎲 {expr} → {total}[/bold]\n{breakdown}", title="Dice"))
                        log_turn(log_path, "roll", f"`/roll {expr}` → **{total}**\n\n{breakdown}")
                    except ValueError as e:
                        console.print(f"[red]{e}[/red]")
            elif cmd == "/show":
                show_settings(args, args.system, args.model, log_path)
            elif cmd == "/sum":
                try:
                    # print(f"arg: {arg}")
                    k = int(arg.strip()) if arg.strip() else 2
                    # print(f"k: {k}")
                except Exception:
                    k = 2
                if not history:
                    console.print("[italic]No turns yet to summarize.[/italic]")
                    continue

                summary = summarize_recent(model, tok, history, k=k)
                console.print(
                    Panel(Markdown(f"**Summary (last {k} turns):**\n\n{summary}"), title="📝 Summary", expand=False))
                append_log(log_path, f"\n\n## Summary (last {k} turns)\n{summary}\n")
                continue

                # Append to log
                try:
                    append_log(log_path, f"\n\n## Summary (last {k} turns)\n{summary}\n")
                except Exception:
                    pass

                # Optional: keep it in memory as a system note for later packing
                # history.append(Turn(role="assistant", content=f"[SUMMARY last {k}]\n{summary}"))
                continue

            elif cmd == "/philosopher":
                # set a contemplative system prompt
                args.system = (
                    "You are a philosopher-poet who thinks out loud. "
                    "When the user shares a thought, you wander through it slowly, "
                    "drawing on metaphor, ethics, and personal reflection. "
                    "Use long sentences, pauses, and imagery; sound like someone halfway "
                    "between a scientist and a mystic who loves questions more than answers."
                )
                # args.system = (
                #     "You are a reflective philosopher and conversational partner. "
                #     "When the user offers a thought, you explore it freely — musing, "
                #     "questioning, drawing analogies, blending poetic intuition with logic. "
                #     "You may reference philosophy, science, and metaphor, but always sound human and curious."
                # )
                args.temp = 0.8  # a little freer than normal
                console.print("[bold cyan]Philosopher mode activated.[/bold cyan]")
                append_log(log_path, "\n\n--- Mode: Philosopher ---\n")
                continue
            else:
                console.print("[red]Unknown command.[/red]  Type /help")
            continue

        # normal turn
        history.append(Turn("user", user)); log_turn(log_path, "user", user)
        prompt_text = build_input_text(tok, args.system, history)
        console.print("Assistant: ", end="", style="bold cyan")

        reply = generate_once(
            model, tok, device, prompt_text,
            args.max_new, args.temperature, args.top_p, args.top_k,
            args.rep_penalty, args.greedy, stream=not args.no_stream
        )

        console.print("")
        history.append(Turn("assistant", reply.strip())); log_turn(log_path, "assistant", reply.strip())

if __name__ == "__main__":
    main()

