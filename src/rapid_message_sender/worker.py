import sys
import time
import ctypes
import logging
from PySide6.QtCore import QThread, Signal
import pyautogui
import pyperclip

from rapid_message_sender.config import SenderConfig

logger = logging.getLogger(__name__)

# Configure PyAutoGUI settings for high stability
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.005

def clear_system_clipboard():
    """Completely empties system clipboard buffer."""
    try:
        pyperclip.copy("")
    except Exception:
        pass
    
    if sys.platform == "win32":
        try:
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
                ctypes.windll.user32.CloseClipboard()
        except Exception:
            pass

class MessageWorker(QThread):
    """Worker thread running verified clipboard paste sequence off the main UI loop."""
    countdown_tick = Signal(int)
    sending_started = Signal()
    progress_updated = Signal(int, int, str)
    finished = Signal(int, float)
    stopped = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, config: SenderConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self._stop_requested = False

    def request_stop(self):
        self._stop_requested = True

    def _copy_and_paste(self, payload: str, send_key: str):
        """
        Copies payload to system clipboard, verifies update, pastes via PyAutoGUI,
        and triggers send key with micro-pauses to prevent OS clipboard locks and skipped lines.
        """
        # Step 1: Copy with retry to guarantee OS clipboard buffer update
        for _ in range(5):
            try:
                pyperclip.copy(payload)
                time.sleep(0.005)  # 5ms OS clipboard buffer flush
                break
            except Exception:
                time.sleep(0.005)

        # Step 2: Trigger Paste
        pyautogui.hotkey('ctrl', 'v')

        # Step 3: Micro-pause to allow target chat window to process WM_PASTE event
        time.sleep(0.012)

        # Step 4: Execute Send Key
        if send_key == "enter":
            pyautogui.press('enter')
        elif send_key == "ctrl+enter":
            pyautogui.hotkey('ctrl', 'enter')
        elif send_key == "shift+enter":
            pyautogui.hotkey('shift', 'enter')

        # Step 5: Brief micro-pause post-send
        time.sleep(0.005)

    def run(self):
        self._stop_requested = False
        start_time = time.time()
        sent_count = 0

        # Backup clipboard if configured
        previous_clipboard = ""
        if self.config.restore_clipboard:
            try:
                previous_clipboard = pyperclip.paste()
            except Exception:
                pass

        try:
            # Countdown delay phase
            delay_sec = max(0, self.config.start_delay_sec)
            for seconds_left in range(delay_sec, 0, -1):
                if self._stop_requested:
                    self.stopped.emit(0)
                    return
                self.countdown_tick.emit(seconds_left)
                
                # Check cancellation in small 100ms intervals
                for _ in range(10):
                    if self._stop_requested:
                        self.stopped.emit(0)
                        return
                    time.sleep(0.1)

            self.countdown_tick.emit(0)
            if self._stop_requested:
                self.stopped.emit(0)
                return

            self.sending_started.emit()

            # Message dispatch loop
            total = self.config.count
            interval_sec = max(0.001, self.config.interval_ms / 1000.0)
            send_key = self.config.send_key.lower()

            for i in range(1, total + 1):
                if self._stop_requested:
                    break

                # Form payload text
                if self.config.show_counter:
                    sep = self.config.counter_separator
                    if self.config.counter_position == "after":
                        payload = f"{self.config.message}{sep}{i}"
                    else:
                        payload = f"{i}{sep}{self.config.message}"
                else:
                    payload = self.config.message

                # Execute verified clipboard copy, paste & send key
                self._copy_and_paste(payload, send_key)

                sent_count += 1
                self.progress_updated.emit(sent_count, total, payload)

                # Micro-sleep interval for fast response to abort signals
                end_time = time.time() + interval_sec
                while time.time() < end_time:
                    if self._stop_requested:
                        break
                    time.sleep(min(0.005, max(0.0, end_time - time.time())))

            elapsed = time.time() - start_time
            if self._stop_requested:
                self.stopped.emit(sent_count)
            else:
                self.finished.emit(sent_count, elapsed)

        except Exception as err:
            logger.exception("Error during message automation")
            self.error_occurred.emit(str(err))
        finally:
            time.sleep(0.02)
            if self.config.restore_clipboard and previous_clipboard:
                try:
                    pyperclip.copy(previous_clipboard)
                except Exception:
                    clear_system_clipboard()
            else:
                clear_system_clipboard()
