import logging
from PySide6.QtCore import QObject, Signal
from pynput import keyboard

logger = logging.getLogger(__name__)

class GlobalHotkeyListener(QObject):
    """System-wide keyboard listener monitoring Ctrl+Q hotkey."""
    hotkey_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listener = None

    def start(self):
        if self._listener is not None:
            return

        try:
            hotkeys = {
                '<ctrl>+q': self._on_triggered,
                '<ctrl>+Q': self._on_triggered,
            }
            self._listener = keyboard.GlobalHotKeys(hotkeys)
            self._listener.daemon = True
            self._listener.start()
        except Exception as err:
            logger.warning(f"Could not bind global keyboard hotkeys: {err}")

    def stop(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def _on_triggered(self):
        self.hotkey_triggered.emit()
