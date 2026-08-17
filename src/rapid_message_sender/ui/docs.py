from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QGroupBox, QGridLayout
)

class DocumentationWidget(QWidget):
    """Modern User Guide & Documentation Page Widget."""
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header card with Back button
        header_card = QFrame()
        header_card.setObjectName("Card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(18, 14, 18, 14)

        title_vbox = QVBoxLayout()
        title_label = QLabel("📖 User Guide & Documentation")
        title_label.setObjectName("SectionTitle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        subtitle_label = QLabel("Complete step-by-step instructions, safety shortcuts, and automation tips")
        subtitle_label.setObjectName("Subtitle")

        title_vbox.addWidget(title_label)
        title_vbox.addWidget(subtitle_label)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()

        back_btn = QPushButton("🔙 Back to Main App")
        back_btn.setObjectName("PrimaryButton")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)

        main_layout.addWidget(header_card)

        # Content Card with Scroll Area
        content_card = QFrame()
        content_card.setObjectName("Card")
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(18, 18, 18, 18)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        # -------------------------------------------------------------
        # Section 1: Quick Start Guide (6-Step Tutorial)
        # -------------------------------------------------------------
        guide_group = QGroupBox("🚀 Quick Start Tutorial")
        guide_vbox = QVBoxLayout(guide_group)
        guide_vbox.setSpacing(14)

        steps = [
            ("1️⃣ Step 1: Message Content", "Enter your single or multi-line message in the text editor. You can also pick preset templates from the dropdown menu."),
            ("2️⃣ Step 2: Choose Input Method", "Select '⌨️ Direct Character Typing' (simulates real keyboard typing without touching clipboard) or '⚡ Clipboard Copy & Paste' (ultra-fast)."),
            ("3️⃣ Step 3: Configure Automation", "Set 'How many times send' (e.g. 10), 'Wait between each message' (default 100 ms), and 'Start countdown delay' (default 5 sec)."),
            ("4️⃣ Step 4: Counter & Options", "Check 'Show counter after message' if you want automatic numbering ('Hello 1', 'Hello 2'...). Select your preferred separator and position."),
            ("5️⃣ Step 5: Start & Focus Target", "Click '🚀 Start Sending'. During the 5-second countdown, switch focus immediately to your target chat box (WhatsApp, Telegram, Discord, Messenger, Notepad, etc.)."),
            ("6️⃣ Step 6: Emergency Stop (Ctrl + Q)", "If you need to stop sending at any time, press 'Ctrl + Q' on your keyboard. It works globally from any window!")
        ]

        for step_title, step_desc in steps:
            box = QFrame()
            box.setObjectName("StatBox")
            box_vbox = QVBoxLayout(box)
            box_vbox.setContentsMargins(12, 10, 12, 10)

            st_lbl = QLabel(step_title)
            st_lbl.setStyleSheet("font-weight: 700; color: #38BDF8; font-size: 14px;")
            sd_lbl = QLabel(step_desc)
            sd_lbl.setStyleSheet("color: #E2E8F0; font-size: 12px; margin-top: 4px;")
            sd_lbl.setWordWrap(True)

            box_vbox.addWidget(st_lbl)
            box_vbox.addWidget(sd_lbl)
            guide_vbox.addWidget(box)

        scroll_layout.addWidget(guide_group)

        # -------------------------------------------------------------
        # Section 2: Key Features & Reliability Enhancements
        # -------------------------------------------------------------
        features_group = QGroupBox("🛡️ Built-in Reliability & Safety Features")
        features_grid = QGridLayout(features_group)
        features_grid.setSpacing(12)

        feat_items = [
            ("⌨️ Direct Character Typing Engine", "Simulates direct hardware keyboard keystrokes via OS pynput controller, bypassing clipboard memory completely."),
            ("⚡ Clipboard Copy-Paste Engine", "Uses PyAutoGUI Ctrl+V with strict read-back verification and Win32 fallback for ultra-fast multi-line pasting."),
            ("🔄 GitHub Release Auto-Updater", "Asynchronously queries GitHub for new releases, downloads updates, replaces old EXE, and deletes old files automatically upon restart."),
            ("🚨 Dual Emergency Abort", "Press Ctrl+Q globally from any app or move your mouse cursor to the top-left corner (PyAutoGUI Fail-Safe) to stop sending instantly."),
            ("🔒 Mouse Scroll Lock", "Prevents accidental changes to spinboxes and dropdowns when scrolling over input settings."),
            ("🔄 Reset All Button", "Restores all defaults, settings, log previews, and clipboard memory with a single click.")
        ]

        row, col = 0, 0
        for f_title, f_desc in feat_items:
            f_box = QFrame()
            f_box.setObjectName("StatBox")
            f_vbox = QVBoxLayout(f_box)
            f_vbox.setContentsMargins(12, 10, 12, 10)

            ft_lbl = QLabel(f_title)
            ft_lbl.setStyleSheet("font-weight: 700; color: #818CF8; font-size: 13px;")
            fd_lbl = QLabel(f_desc)
            fd_lbl.setStyleSheet("color: #CBD5E1; font-size: 11px; margin-top: 4px;")
            fd_lbl.setWordWrap(True)

            f_vbox.addWidget(ft_lbl)
            f_vbox.addWidget(fd_lbl)
            features_grid.addWidget(f_box, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

        scroll_layout.addWidget(features_group)

        # -------------------------------------------------------------
        # Section 3: Keyboard Shortcuts Summary Table
        # -------------------------------------------------------------
        shortcuts_group = QGroupBox("⌨️ Shortcuts & Hotkey Reference")
        shortcuts_vbox = QVBoxLayout(shortcuts_group)

        table_box = QFrame()
        table_box.setObjectName("StatBox")
        table_layout = QGridLayout(table_box)
        table_layout.setSpacing(10)

        rows = [
            ("Ctrl + Q", "Global Emergency Abort (Works across all Windows applications)"),
            ("Enter", "Standard trigger key sent after typing/pasting payload"),
            ("Ctrl + Enter", "Alternative send trigger (for apps like Discord/Slack multi-line settings)"),
            ("Shift + Enter", "Newline insertion without instant sending"),
            ("None", "Type or paste message payload into input field without pressing any trigger key"),
            ("Top-Left Screen Corner", "PyAutoGUI hardware Mouse Fail-Safe abort")
        ]

        for idx, (hk, desc) in enumerate(rows):
            hk_lbl = QLabel(hk)
            hk_lbl.setStyleSheet("font-weight: 800; color: #00F2FE; font-size: 12px; background: rgba(0,242,254,0.1); padding: 4px 8px; border-radius: 4px;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("color: #E2E8F0; font-size: 12px;")

            table_layout.addWidget(hk_lbl, idx, 0)
            table_layout.addWidget(desc_lbl, idx, 1)

        shortcuts_vbox.addWidget(table_box)
        scroll_layout.addWidget(shortcuts_group)

        scroll.setWidget(scroll_content)
        card_layout.addWidget(scroll)
        main_layout.addWidget(content_card)
