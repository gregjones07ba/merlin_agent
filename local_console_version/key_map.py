from prompt_toolkit.key_binding import KeyBindings

class KeyMap:
    def __init__(self):
        self.kb = KeyBindings()

        @self.kb.add("tab")
        def _(event):
            b = event.app.current_buffer
            b.start_completion(select_first=True)

        def _send(event):
            b = event.app.current_buffer
            if b.complete_state:
                b.cancel_completion()
            b.validate_and_handle()

        @self.kb.add("enter")   # a.k.a. "return" on some terminals
        def _(event):
            _send(event)

        @self.kb.add("c-j")     # Ctrl+J inserts newline
        def _(event):
            event.app.current_buffer.insert_text("\n")
