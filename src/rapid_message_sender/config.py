from dataclasses import dataclass

@dataclass
class SenderConfig:
    message: str = "Hello! This is an automated rapid message."
    count: int = 10
    interval_ms: int = 100
    start_delay_sec: int = 5
    show_counter: bool = True
    counter_separator: str = " "
    counter_position: str = "after"  # "after" or "before"
    send_key: str = "enter"  # "enter", "ctrl+enter", "shift+enter", or "none"
    restore_clipboard: bool = True
