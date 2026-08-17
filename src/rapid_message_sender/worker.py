import sys
import time
import ctypes
import logging
from PySide6.QtCore import QThread, Signal
import pyautogui
import pyperclip
from pynput.keyboard import Controller as KeyboardController

from rapid_message_sender.config import SenderConfig

logger = logging.getLogger(__name__)

# Configure PyAutoGUI settings for high stability
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.005

_keyboard_controller = KeyboardController()


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
    """Worker thread running direct typing or clipboard paste sequence off the main UI loop."""
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

    def _direct_typewrite(self, payload: str, send_key: str):
        """
        Types payload directly into active focus box via OS hardware keyboard simulation (pynput)
        without using or modifying the system clipboard.
        """
        # Step 1: Release any stuck modifier keys
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('alt')
        pyautogui.keyUp('shift')

        # Step 2: Direct character typing simulation
        try:
            _keyboard_controller.type(payload)
        except Exception:
            pyautogui.write(payload, interval=0.001)

        time.sleep(0.010)

        # Step 3: Trigger Send Key
        if send_key == "enter":
            pyautogui.press('enter')
        elif send_key == "ctrl+enter":
            pyautogui.keyDown('ctrl')
            pyautogui.press('enter')
            pyautogui.keyUp('ctrl')
        elif send_key == "shift+enter":
            pyautogui.keyDown('shift')
            pyautogui.press('enter')
            pyautogui.keyUp('shift')

        # Step 4: Release modifier keys post-send
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')
        time.sleep(0.006)

    def _win32_set_clipboard_text(self, text: str):
        """Direct Win32 API clipboard writer for fallback if OS clipboard gets locked."""
        if sys.platform != "win32":
            return
        
        CF_UNICODETEXT = 13
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        for _ in range(5):
            if user32.OpenClipboard(None):
                user32.EmptyClipboard()
                encoded = text.encode("utf-16le") + b"\x00\x00"
                h_mem = kernel32.GlobalAlloc(0x0042, len(encoded))
                if h_mem:
                    p_mem = kernel32.GlobalLock(h_mem)
                    ctypes.memmove(p_mem, encoded, len(encoded))
                    kernel32.GlobalUnlock(h_mem)
                    user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                user32.CloseClipboard()
                break
            time.sleep(0.003)

    def _copy_and_paste(self, payload: str, send_key: str):
        """
        Copies payload to system clipboard with strict read-back verification,
        pastes via Ctrl+V, and triggers send key without modifier key bleed or skipped lines.
        """
        # Step 1: Verified Clipboard Copy (Retry until read-back matches payload 100%)
        copied_successfully = False
        for _ in range(12):
            try:
                pyperclip.copy(payload)
                time.sleep(0.003)
                if pyperclip.paste() == payload:
                    copied_successfully = True
                    break
            except Exception:
                time.sleep(0.003)

        # Fallback to direct Win32 API if pyperclip fails to lock clipboard
        if not copied_successfully:
            try:
                self._win32_set_clipboard_text(payload)
                time.sleep(0.004)
            except Exception as e:
                logger.warning(f"Win32 clipboard fallback exception: {e}")

        time.sleep(0.004)

        # Step 2: Release any stuck modifier keys before pasting
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('alt')
        pyautogui.keyUp('shift')

        # Step 3: Explicit Paste Key Sequence
        pyautogui.keyDown('ctrl')
        pyautogui.press('v')
        pyautogui.keyUp('ctrl')

        # Step 4: Micro-pause to allow target chat window to process WM_PASTE event
        time.sleep(0.015)

        # Step 5: Execute Send Key safely without modifier key interference
        if send_key == "enter":
            pyautogui.press('enter')
        elif send_key == "ctrl+enter":
            pyautogui.keyDown('ctrl')
            pyautogui.press('enter')
            pyautogui.keyUp('ctrl')
        elif send_key == "shift+enter":
            pyautogui.keyDown('shift')
            pyautogui.press('enter')
            pyautogui.keyUp('shift')

        # Release modifier keys post-send
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')

        # Step 6: Brief post-send micro-pause
        time.sleep(0.006)

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
            interval_sec = max(0.100, self.config.interval_ms / 1000.0)
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

                # Execute based on configured input_mode
                if self.config.input_mode == "paste":
                    self._copy_and_paste(payload, send_key)
                else:
                    self._direct_typewrite(payload, send_key)

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
