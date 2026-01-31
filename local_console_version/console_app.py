import argparse
import random
from rich.console import Console
import time
import torch
from typing import List, Optional

class ConsoleApp:
    def __init__(self):
        self.console = Console(highlight=False)

        self.args = self.build_parser().parse_args()

        device = "mps" if (self.args.device or self.pick_device(None)) == "mps" else "cpu"
        dtype = torch.float16 if (self.args.dtype == "float16" or (self.args.dtype == "auto" and device == "mps")) else \
            torch.bfloat16 if self.args.dtype == "bfloat16" else \
                torch.float32

        self.console.print(f"[bold]device:[/bold] {device}")
        self.set_seed_everywhere(self.args.seed or (time.time_ns() & 0x7FFFFFFF))

    def build_parser(self):
        p = argparse.ArgumentParser(
            description="Local instruct-model chat (Transformers + MPS) with logs, commands, colors, multiline input",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument("-m", "--model", default="meta-llama/Llama-3.1-8B-Instruct", help="HF model id or local path")
        p.add_argument(
            "--system",
            default=("You are a master storyteller who co-creates stories with the user. "
                     "Your tone is vivid, emotional, and adaptable—shift genres as directed. "
                     "After each user message, continue the story naturally."),
            help="System message / persona",
        )
        p.add_argument("--device", choices=["mps", "cpu"], default=None, help="Force device (default: auto)")
        p.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="auto")
        p.add_argument("--greedy", action="store_true", help="Disable sampling")
        p.add_argument("--no-stream", action="store_true", help="Disable streaming output")
        p.add_argument("--seed", type=int, default=0, help="RNG seed (0 = random)")
        p.add_argument("--temperature", type=float, default=0.7)
        p.add_argument("--top-p", type=float, default=0.9, dest="top_p")
        p.add_argument("--top-k", type=int, default=40, dest="top_k")
        p.add_argument("--rep-penalty", type=float, default=1.05, dest="rep_penalty")
        p.add_argument("-x", "--max-new", type=int, default=None, help="Max new tokens (adaptive if omitted)")
        return p

    def pick_device(self, user_choice: Optional[str]) -> str:
        if user_choice:
            return user_choice
        return "mps" if torch.backends.mps.is_available() else "cpu"

    def set_seed_everywhere(self, seed: int):
        if seed and seed > 0:
            torch.manual_seed(seed)
            try:
                import numpy as np
                random.seed(seed);
                np.random.seed(seed)
            except Exception:
                pass


