import os
import sys
import logging
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QSpinBox, QCheckBox, QPushButton, QProgressBar, QFrame,
    QComboBox, QFormLayout, QMessageBox, QGroupBox, QScrollArea,
    QSizePolicy, QGridLayout, QStackedWidget, QProgressDialog
)

from rapid_message_sender.config import SenderConfig
from rapid_message_sender.worker import MessageWorker, clear_system_clipboard
from rapid_message_sender.hotkey import GlobalHotkeyListener
from rapid_message_sender.ui.theme import get_stylesheet
from rapid_message_sender.ui.docs import DocumentationWidget
from rapid_message_sender.ui.icon import get_app_icon
from rapid_message_sender.updater import (
    UpdateCheckWorker, DownloadUpdateWorker, apply_update_and_restart, CURRENT_VERSION
)

logger = logging.getLogger(__name__)


class NoWheelSpinBox(QSpinBox):
    """QSpinBox subclass that ignores mouse wheel events to prevent accidental value changes on scroll."""
    def wheelEvent(self, event):
        event.ignore()


class NoWheelComboBox(QComboBox):
    """QComboBox subclass that ignores mouse wheel events to prevent accidental option changes on scroll."""
    def wheelEvent(self, event):
        event.ignore()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Rapid Message Sender ({CURRENT_VERSION})")
        self.setMinimumSize(1200, 720)
        self.resize(1200, 720)

        # Set application window icon
        self.setWindowIcon(get_app_icon())

        self.worker = None
        self.hotkey_listener = None
        self.check_worker = None

        self._build_ui()
        self._setup_hotkeys()
        self.setStyleSheet(get_stylesheet())

        # Check for updates silently on launch
        self._check_updates(silent=True)

    def _build_ui(self):
        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header bar
        header_card = QFrame()
        header_card.setObjectName("Card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(18, 14, 18, 14)

        title_vbox = QVBoxLayout()
        title_label = QLabel("⚡ Rapid Message Sender")
        title_label.setObjectName("SectionTitle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))

        title_vbox.addWidget(title_label)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()

        # Update Checker Button
        self.update_btn = QPushButton("🔄 Check Updates")
        self.update_btn.setObjectName("SecondaryButton")
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.clicked.connect(lambda: self._check_updates(silent=False))
        header_layout.addWidget(self.update_btn)

        # Documentation Page Button
        self.docs_btn = QPushButton("📖 User Guide")
        self.docs_btn.setObjectName("SecondaryButton")
        self.docs_btn.setCursor(Qt.PointingHandCursor)
        self.docs_btn.clicked.connect(self._show_documentation)
        header_layout.addWidget(self.docs_btn)

        shortcut_badge = QLabel("🔥 Emergency Stop: Ctrl + Q")
        shortcut_badge.setObjectName("BadgeHeader")
        header_layout.addWidget(shortcut_badge)

        layout.addWidget(header_card)

        # Stacked Widget for Page Navigation (Workspace vs Documentation)
        self.stacked_widget = QStackedWidget()

        # PAGE 0: Main Workspace Widget
        workspace_widget = QWidget()
        body_layout = QHBoxLayout(workspace_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(16)

        # Left panel: Configuration controls
        left_card = QFrame()
        left_card.setObjectName("Card")
        left_vbox = QVBoxLayout(left_card)
        left_vbox.setContentsMargins(18, 18, 18, 18)
        left_vbox.setSpacing(16)

        # Message editor header
        msg_header = QHBoxLayout()
        msg_title = QLabel("💬 Message Content")
        msg_title.setObjectName("SectionTitle")
        msg_header.addWidget(msg_title)
        msg_header.addStretch()

        self.preset_combo = NoWheelComboBox()
        self.preset_combo.addItems([
            "Select Template...",
            "Hello World!",
            "🔥 Rapid Message Sender Test!",
            "Reminder: Please check your inbox.",
            "Multi-line Sample:\nLine 1\nLine 2"
        ])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        msg_header.addWidget(self.preset_combo)
        left_vbox.addLayout(msg_header)

        self.msg_edit = QTextEdit()
        self.msg_edit.setPlaceholderText("Type your message here...")
        self.msg_edit.setMinimumHeight(110)
        self.msg_edit.setText("Hello! This is a rapid automated message.")
        left_vbox.addWidget(self.msg_edit)

        # Automation settings form
        settings_group = QGroupBox("⚙️ Automation Settings")
        form_layout = QFormLayout(settings_group)
        form_layout.setVerticalSpacing(16)
        form_layout.setHorizontalSpacing(18)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        lbl_input_mode = QLabel("Input Method:")
        self.input_mode_combo = NoWheelComboBox()
        self.input_mode_combo.addItems([
            "⌨️ Direct Character Typing (Simulated Keyboard)",
            "⚡ Clipboard Copy & Paste (Ultra-Fast)"
        ])

        lbl_count = QLabel("How many times send:")
        self.count_spin = NoWheelSpinBox()
        self.count_spin.setRange(1, 100000)
        self.count_spin.setValue(10)

        lbl_interval = QLabel("Wait between each message:")
        self.interval_spin = NoWheelSpinBox()
        self.interval_spin.setRange(1, 60000)
        self.interval_spin.setSingleStep(10)
        self.interval_spin.setValue(100)
        self.interval_spin.setSuffix(" ms")

        lbl_start_delay = QLabel("Start countdown delay:")
        self.start_delay_spin = NoWheelSpinBox()
        self.start_delay_spin.setRange(0, 300)
        self.start_delay_spin.setValue(5)
        self.start_delay_spin.setSuffix(" sec")

        lbl_send_key = QLabel("Trigger Key after Typing:")
        self.send_key_combo = NoWheelComboBox()
        self.send_key_combo.addItems([
            "Enter (Standard Send)",
            "Ctrl + Enter",
            "Shift + Enter",
            "None (Type Only)"
        ])

        # Apply expanding width to ensure all inputs match width exactly
        for widget in (self.input_mode_combo, self.count_spin, self.interval_spin, self.start_delay_spin, self.send_key_combo):
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        form_layout.addRow(lbl_input_mode, self.input_mode_combo)
        form_layout.addRow(lbl_count, self.count_spin)
        form_layout.addRow(lbl_interval, self.interval_spin)
        form_layout.addRow(lbl_start_delay, self.start_delay_spin)
        form_layout.addRow(lbl_send_key, self.send_key_combo)

        left_vbox.addWidget(settings_group)

        # Counter options box
        counter_group = QGroupBox("🔢 Counter Options")
        counter_vbox = QVBoxLayout(counter_group)
        counter_vbox.setSpacing(12)

        self.counter_checkbox = QCheckBox("Show counter after message (e.g. 'message 1', 'message 2'...)")
        self.counter_checkbox.setChecked(True)
        counter_vbox.addWidget(self.counter_checkbox)

        counter_row = QHBoxLayout()
        counter_row.setSpacing(10)
        
        lbl_sep = QLabel("Separator:")
        self.sep_combo = NoWheelComboBox()
        self.sep_combo.addItems(["Space (' ')", "Semicolon ('; ')", "Dash (' - ')", "Hash (' #')"])
        self.sep_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lbl_pos = QLabel("Position:")
        self.pos_combo = NoWheelComboBox()
        self.pos_combo.addItems(["After Message", "Before Message"])
        self.pos_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        counter_row.addWidget(lbl_sep)
        counter_row.addWidget(self.sep_combo)
        counter_row.addWidget(lbl_pos)
        counter_row.addWidget(self.pos_combo)

        counter_vbox.addLayout(counter_row)
        left_vbox.addWidget(counter_group)

        self.restore_clip_cb = QCheckBox("Restore original clipboard text when done")
        self.restore_clip_cb.setChecked(True)
        left_vbox.addWidget(self.restore_clip_cb)

        # Scroll area for left configuration panel
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setWidget(left_card)

        body_layout.addWidget(left_scroll, stretch=5)

        # Right panel: Dashboard & Status Controls
        right_card = QFrame()
        right_card.setObjectName("Card")
        right_vbox = QVBoxLayout(right_card)
        right_vbox.setContentsMargins(18, 18, 18, 18)
        right_vbox.setSpacing(14)

        dash_title = QLabel("📊 Status & Controls")
        dash_title.setObjectName("SectionTitle")
        right_vbox.addWidget(dash_title)

        # Banner status card
        self.banner = QFrame()
        self.banner.setObjectName("CountdownBanner")
        banner_layout = QVBoxLayout(self.banner)
        banner_layout.setContentsMargins(12, 12, 12, 12)

        self.status_lbl = QLabel("READY TO SEND")
        self.status_lbl.setStyleSheet("color: #10B981; font-weight: 800; font-size: 13px; background: transparent;")

        self.banner_txt = QLabel("Press 'Start Sending' to begin")
        self.banner_txt.setObjectName("CountdownText")
        self.banner_txt.setAlignment(Qt.AlignCenter)

        banner_layout.addWidget(self.status_lbl, 0, Qt.AlignCenter)
        banner_layout.addWidget(self.banner_txt, 0, Qt.AlignCenter)
        right_vbox.addWidget(self.banner)

        # Quick stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)

        stat1_box = QFrame()
        stat1_box.setObjectName("StatBox")
        s1_vbox = QVBoxLayout(stat1_box)
        s1_vbox.setContentsMargins(8, 8, 8, 8)
        self.stat_sent_val = QLabel("0 / 0")
        self.stat_sent_val.setObjectName("StatValue")
        s1_lbl = QLabel("Messages Sent")
        s1_lbl.setObjectName("StatLabel")
        s1_vbox.addWidget(self.stat_sent_val)
        s1_vbox.addWidget(s1_lbl)
        stats_grid.addWidget(stat1_box, 0, 0)

        stat2_box = QFrame()
        stat2_box.setObjectName("StatBox")
        s2_vbox = QVBoxLayout(stat2_box)
        s2_vbox.setContentsMargins(8, 8, 8, 8)
        self.stat_time_val = QLabel("0.0 s")
        self.stat_time_val.setObjectName("StatValue")
        s2_lbl = QLabel("Elapsed Time")
        s2_lbl.setObjectName("StatLabel")
        s2_vbox.addWidget(self.stat_time_val)
        s2_vbox.addWidget(s2_lbl)
        stats_grid.addWidget(stat2_box, 0, 1)

        right_vbox.addLayout(stats_grid)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% Completed")
        right_vbox.addWidget(self.progress_bar)

        log_lbl = QLabel("📝 Live Preview Logs")
        log_lbl.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px; background: transparent;")
        right_vbox.addWidget(log_lbl)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Message dispatch logs will appear here...")
        self.log_text.setStyleSheet("QTextEdit { font-family: Consolas, monospace; font-size: 11px; background-color: #0D0F14; }")
        right_vbox.addWidget(self.log_text, stretch=1)

        # Action buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        self.start_btn = QPushButton("🚀 Start Sending")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._start_sending)

        self.stop_btn = QPushButton("🛑 STOP (Ctrl+Q)")
        self.stop_btn.setObjectName("StopButton")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_sending)

        self.reset_btn = QPushButton("🔄 Reset All")
        self.reset_btn.setObjectName("SecondaryButton")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self._reset_everything)

        btn_box.addWidget(self.start_btn, stretch=3)
        btn_box.addWidget(self.stop_btn, stretch=2)
        btn_box.addWidget(self.reset_btn, stretch=2)

        right_vbox.addLayout(btn_box)

        body_layout.addWidget(right_card, stretch=4)
        self.stacked_widget.addWidget(workspace_widget)  # Index 0

        # PAGE 1: Documentation Widget
        self.docs_widget = DocumentationWidget()
        self.docs_widget.back_requested.connect(self._show_workspace)
        self.stacked_widget.addWidget(self.docs_widget)  # Index 1

        layout.addWidget(self.stacked_widget)

    def _show_documentation(self):
        self.stacked_widget.setCurrentIndex(1)
        self.docs_btn.setText("⚡ Back to App")
        try:
            self.docs_btn.clicked.disconnect()
        except Exception:
            pass
        self.docs_btn.clicked.connect(self._show_workspace)

    def _show_workspace(self):
        self.stacked_widget.setCurrentIndex(0)
        self.docs_btn.setText("📖 User Guide")
        try:
            self.docs_btn.clicked.disconnect()
        except Exception:
            pass
        self.docs_btn.clicked.connect(self._show_documentation)

    # -----------------------------------------------------------------
    # Update Checking & Installer Flow
    # -----------------------------------------------------------------
    def _check_updates(self, silent: bool = False):
        self._update_silent = silent
        if not silent:
            self.update_btn.setEnabled(False)
            self.update_btn.setText("🔄 Checking...")
            self.log_text.append("🔎 Checking GitHub for latest release...")

        self.check_worker = UpdateCheckWorker(self)
        self.check_worker.update_available.connect(self._on_update_available)
        self.check_worker.no_update_found.connect(self._on_no_update_found)
        self.check_worker.check_failed.connect(self._on_update_check_failed)
        self.check_worker.start()

    def _reset_update_btn(self):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("🔄 Check Updates")

    def _on_no_update_found(self, current_ver: str):
        self._reset_update_btn()
        if not getattr(self, "_update_silent", False):
            self.log_text.append(f"✅ You are using the latest version ({current_ver}).")
            QMessageBox.information(
                self,
                "No Updates Available",
                f"You are already using the latest version ({current_ver})."
            )

    def _on_update_check_failed(self, error_msg: str):
        self._reset_update_btn()
        if not getattr(self, "_update_silent", False):
            self.log_text.append(f"⚠️ Update check notice: {error_msg}")
            QMessageBox.warning(
                self,
                "Update Check Notice",
                f"Could not query GitHub updates:\n{error_msg}"
            )

    def _on_update_available(self, release_info: dict):
        self._reset_update_btn()
        tag_name = release_info.get("tag_name", "New Release")
        notes = release_info.get("body", "No release notes provided.")
        download_url = release_info.get("download_url")

        self.log_text.append(f"🎉 New version available on GitHub: {tag_name}")

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("🎉 Update Available!")
        msg_box.setText(f"<h3>A new release ({tag_name}) is available!</h3>Current version: <b>{CURRENT_VERSION}</b>")

        preview_notes = notes[:300] + ("..." if len(notes) > 300 else "")
        msg_box.setInformativeText(f"<b>Changelog:</b><br><pre>{preview_notes}</pre><br>Would you like to update now?")

        update_btn = msg_box.addButton("🚀 Update Now", QMessageBox.AcceptRole)
        later_btn = msg_box.addButton("Later", QMessageBox.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == update_btn:
            if download_url:
                self._start_download_update(download_url, tag_name)
            else:
                # If no EXE asset attached, open GitHub release page in browser
                QDesktopServices.openUrl(QUrl(release_info.get("html_url", "")))

    def _start_download_update(self, download_url: str, tag_name: str):
        import tempfile
        save_path = os.path.join(tempfile.gettempdir(), f"RapidMessageSender_{tag_name}.exe")

        progress_dialog = QProgressDialog("Downloading latest release...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Updating Rapid Message Sender")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)

        dl_worker = DownloadUpdateWorker(download_url, save_path, self)

        def on_progress(downloaded, total):
            if total > 0:
                pct = int((downloaded / total) * 100)
                progress_dialog.setValue(pct)
                progress_dialog.setLabelText(f"Downloading update ({downloaded // 1024} KB / {total // 1024} KB)...")

        def on_finished(new_exe_path):
            progress_dialog.close()
            QMessageBox.information(
                self,
                "Update Ready",
                "Download complete! Click OK to restart and replace the application with the updated version.\n"
                "The old version will be automatically deleted."
            )
            apply_update_and_restart(new_exe_path)

        def on_failed(err_msg):
            progress_dialog.close()
            QMessageBox.critical(self, "Download Failed", f"Failed to download update:\n{err_msg}")

        dl_worker.progress_updated.connect(on_progress)
        dl_worker.download_finished.connect(on_finished)
        dl_worker.download_failed.connect(on_failed)
        progress_dialog.canceled.connect(dl_worker.terminate)

        dl_worker.start()

    # -----------------------------------------------------------------
    # Hotkeys & Controls
    # -----------------------------------------------------------------
    def _setup_hotkeys(self):
        self.qt_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.qt_shortcut.activated.connect(self._stop_sending)

        self.hotkey_listener = GlobalHotkeyListener(self)
        self.hotkey_listener.hotkey_triggered.connect(self._stop_sending)
        self.hotkey_listener.start()

    def _on_preset_changed(self, index: int):
        if index > 0:
            text = self.preset_combo.currentText()
            if "Multi-line" in text:
                self.msg_edit.setText("Line 1\nLine 2\nLine 3")
            else:
                self.msg_edit.setText(text)

    def _get_separator(self) -> str:
        idx = self.sep_combo.currentIndex()
        separators = [" ", "; ", " - ", " #"]
        return separators[idx] if 0 <= idx < len(separators) else " "

    def _start_sending(self):
        message = self.msg_edit.toPlainText()
        if not message and not self.counter_checkbox.isChecked():
            QMessageBox.warning(self, "Validation Error", "Please provide a message to send.")
            return

        self._set_inputs_enabled(False)

        key_mapping = {0: "enter", 1: "ctrl+enter", 2: "shift+enter", 3: "none"}
        input_mode_val = "paste" if self.input_mode_combo.currentIndex() == 1 else "typewrite"

        config = SenderConfig(
            message=message,
            count=self.count_spin.value(),
            interval_ms=self.interval_spin.value(),
            start_delay_sec=self.start_delay_spin.value(),
            show_counter=self.counter_checkbox.isChecked(),
            counter_separator=self._get_separator(),
            counter_position="after" if self.pos_combo.currentIndex() == 0 else "before",
            send_key=key_mapping.get(self.send_key_combo.currentIndex(), "enter"),
            restore_clipboard=self.restore_clip_cb.isChecked(),
            input_mode=input_mode_val
        )

        self.progress_bar.setMaximum(config.count)
        self.progress_bar.setValue(0)
        self.stat_sent_val.setText(f"0 / {config.count}")
        self.stat_time_val.setText("0.0 s")
        self.log_text.clear()
        self.log_text.append(f"🟢 Initialized sender loop ({config.count} messages)...")
        self.log_text.append(f"⌨️ Input Method: {'Direct Typing' if input_mode_val == 'typewrite' else 'Clipboard Paste'}")
        self.log_text.append(f"⏱️ Delay: {config.start_delay_sec}s | Interval: {config.interval_ms}ms")

        self.status_lbl.setText("COUNTDOWN ACTIVE")
        self.status_lbl.setStyleSheet("color: #F59E0B; font-weight: 800; background: transparent;")
        self.banner_txt.setText(f"Starting in {config.start_delay_sec}s... Focus target input box!")

        self.worker = MessageWorker(config)
        self.worker.countdown_tick.connect(self._on_countdown_tick)
        self.worker.sending_started.connect(self._on_sending_started)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.finished.connect(self._on_finished)
        self.worker.stopped.connect(self._on_stopped)
        self.worker.error_occurred.connect(self._on_error)

        self.stop_btn.setEnabled(True)
        self.start_btn.setEnabled(False)
        self.worker.start()

    def _stop_sending(self):
        if self.worker and self.worker.isRunning():
            self.log_text.append("🛑 Stop command received! Aborting...")
            self.worker.request_stop()
            self.stop_btn.setEnabled(False)

    def _reset_everything(self):
        if self.worker and self.worker.isRunning():
            self.worker.request_stop()
            self.worker.wait(1000)

        self.msg_edit.setText("Hello! This is a rapid automated message.")
        self.input_mode_combo.setCurrentIndex(0)
        self.preset_combo.setCurrentIndex(0)
        self.count_spin.setValue(10)
        self.interval_spin.setValue(100)
        self.start_delay_spin.setValue(5)
        self.send_key_combo.setCurrentIndex(0)
        self.counter_checkbox.setChecked(True)
        self.sep_combo.setCurrentIndex(0)
        self.pos_combo.setCurrentIndex(0)
        self.restore_clip_cb.setChecked(True)

        self.progress_bar.setValue(0)
        self.stat_sent_val.setText("0 / 0")
        self.stat_time_val.setText("0.0 s")

        self.status_lbl.setText("READY TO SEND")
        self.status_lbl.setStyleSheet("color: #10B981; font-weight: 800; font-size: 13px; background: transparent;")
        self.banner_txt.setText("Press 'Start Sending' to begin")
        self.log_text.clear()

        clear_system_clipboard()
        self._reset_controls()
        self.log_text.append("🔄 All settings, logs, stats, and active clipboard have been reset.")

    def _on_countdown_tick(self, seconds_left: int):
        if seconds_left > 0:
            self.banner_txt.setText(f"Starting in {seconds_left}s... Focus target input box!")
            self.log_text.append(f"⏳ Countdown: {seconds_left}s remaining...")
        else:
            self.banner_txt.setText("Sending in progress... Press Ctrl+Q to Stop!")

    def _on_sending_started(self):
        self.status_lbl.setText("SENDING IN PROGRESS")
        self.status_lbl.setStyleSheet("color: #00F2FE; font-weight: 800; background: transparent;")
        self.banner_txt.setText("🚀 Sending messages... Keep target window active!")
        self.log_text.append("🚀 Dispatch engine active.")

    def _on_progress_updated(self, current: int, total: int, payload: str):
        self.progress_bar.setValue(current)
        self.stat_sent_val.setText(f"{current} / {total}")
        preview = payload.replace('\n', ' ')
        if len(preview) > 50:
            preview = preview[:47] + "..."
        mode_tag = "Typed" if self.input_mode_combo.currentIndex() == 0 else "Pasted"
        self.log_text.append(f"[{current}/{total}] {mode_tag}: '{preview}'")

    def _on_finished(self, total_sent: int, elapsed: float):
        self.status_lbl.setText("COMPLETED")
        self.status_lbl.setStyleSheet("color: #10B981; font-weight: 800; background: transparent;")
        self.banner_txt.setText(f"✅ Sent {total_sent} messages successfully!")
        self.stat_time_val.setText(f"{elapsed:.1f} s")
        self.log_text.append(f"\n🎉 Finished sending {total_sent} messages in {elapsed:.2f} seconds.")
        self._reset_controls()

    def _on_stopped(self, sent_count: int):
        self.status_lbl.setText("STOPPED BY USER")
        self.status_lbl.setStyleSheet("color: #EF4444; font-weight: 800; background: transparent;")
        self.banner_txt.setText(f"🛑 Aborted after sending {sent_count} messages.")
        self.log_text.append(f"\n⚠️ Process interrupted. Messages sent: {sent_count}.")
        self._reset_controls()

    def _on_error(self, message: str):
        self.status_lbl.setText("ERROR OCCURRED")
        self.status_lbl.setStyleSheet("color: #EF4444; font-weight: 800; background: transparent;")
        self.banner_txt.setText("❌ An error occurred!")
        self.log_text.append(f"\n❌ Error: {message}")
        QMessageBox.critical(self, "Error", f"Automation error occurred:\n{message}")
        self._reset_controls()

    def _reset_controls(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_inputs_enabled(True)

    def _set_inputs_enabled(self, enabled: bool):
        self.msg_edit.setEnabled(enabled)
        self.preset_combo.setEnabled(enabled)
        self.input_mode_combo.setEnabled(enabled)
        self.count_spin.setEnabled(enabled)
        self.interval_spin.setEnabled(enabled)
        self.start_delay_spin.setEnabled(enabled)
        self.send_key_combo.setEnabled(enabled)
        self.counter_checkbox.setEnabled(enabled)
        self.sep_combo.setEnabled(enabled)
        self.pos_combo.setEnabled(enabled)
        self.restore_clip_cb.setEnabled(enabled)

    def closeEvent(self, event):
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.worker and self.worker.isRunning():
            self.worker.request_stop()
            self.worker.wait(1000)
        event.accept()
