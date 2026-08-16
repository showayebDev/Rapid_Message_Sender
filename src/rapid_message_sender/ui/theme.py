import os
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt

def get_checkmark_icon_path() -> str:
    """Creates a checkmark PNG asset if missing and returns QSS-compatible path."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    icon_path = os.path.join(assets_dir, "checkmark.png")

    if not os.path.exists(icon_path):
        pix = QPixmap(20, 20)
        pix.fill(Qt.transparent)
        
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(QColor("#FFFFFF"), 2.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(4, 10, 8, 14)
        painter.drawLine(8, 14, 16, 5)
        painter.end()
        
        pix.save(icon_path, "PNG")

    return icon_path.replace("\\", "/")

def get_arrow_icon_paths() -> tuple[str, str]:
    """Creates up and down arrow PNG assets for QSpinBox if missing."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    up_path = os.path.join(assets_dir, "spin_up.png")
    down_path = os.path.join(assets_dir, "spin_down.png")

    if not os.path.exists(up_path):
        pix = QPixmap(16, 16)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(QColor("#F1F5F9"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(3, 10, 8, 5)
        p.drawLine(8, 5, 13, 10)
        p.end()
        pix.save(up_path, "PNG")

    if not os.path.exists(down_path):
        pix = QPixmap(16, 16)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(QColor("#F1F5F9"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(3, 6, 8, 11)
        p.drawLine(8, 11, 13, 6)
        p.end()
        pix.save(down_path, "PNG")

    return up_path.replace("\\", "/"), down_path.replace("\\", "/")

def get_stylesheet() -> str:
    checkmark_path = get_checkmark_icon_path()
    spin_up_path, spin_down_path = get_arrow_icon_paths()

    return f"""
QWidget {{
    background-color: #0F1117;
    color: #E2E8F0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}}

QLabel {{
    background: transparent;
    background-color: transparent;
    border: none;
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QFrame#Card {{
    background-color: #181B24;
    border: 1px solid #2A2F3D;
    border-radius: 12px;
}}

QLabel#SectionTitle {{
    font-weight: 700;
    font-size: 15px;
    color: #F8FAFC;
}}

QLabel#Subtitle {{
    color: #94A3B8;
    font-size: 12px;
}}

QLabel#BadgeHeader {{
    background-color: rgba(99, 102, 241, 0.15);
    color: #818CF8;
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
}}

QTextEdit, QLineEdit {{
    background-color: #12141C;
    border: 1px solid #2E3446;
    border-radius: 8px;
    padding: 10px 12px;
    color: #F1F5F9;
    selection-background-color: #4F46E5;
    selection-color: #FFFFFF;
    font-size: 13px;
}}

QTextEdit:focus, QLineEdit:focus {{
    border: 1px solid #6366F1;
    background-color: #151824;
}}

QSpinBox {{
    background-color: #12141C;
    border: 1px solid #2E3446;
    border-radius: 8px;
    padding: 6px 36px 6px 12px;
    min-height: 42px;
    color: #F1F5F9;
    font-weight: 600;
    font-size: 14px;
}}

QSpinBox:focus {{
    border: 1px solid #6366F1;
    background-color: #151824;
}}

QSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 28px;
    height: 19px;
    background-color: #1E2330;
    border-top-right-radius: 7px;
    margin-top: 2px;
    margin-right: 2px;
}}

QSpinBox::up-arrow {{
    image: url('{spin_up_path}');
    width: 10px;
    height: 10px;
}}

QSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 28px;
    height: 19px;
    background-color: #1E2330;
    border-bottom-right-radius: 7px;
    margin-bottom: 2px;
    margin-right: 2px;
}}

QSpinBox::down-arrow {{
    image: url('{spin_down_path}');
    width: 10px;
    height: 10px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: #4F46E5;
}}

QComboBox {{
    background-color: #12141C;
    border: 1px solid #2E3446;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 42px;
    color: #F1F5F9;
    font-size: 13px;
}}

QComboBox:focus {{
    border: 1px solid #6366F1;
    background-color: #151824;
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox QAbstractItemView {{
    background-color: #181B24;
    border: 1px solid #2E3446;
    selection-background-color: #4F46E5;
    selection-color: #FFFFFF;
    color: #F1F5F9;
    padding: 6px;
}}

QGroupBox {{
    font-weight: bold;
    border: 1px solid #2A2F3D;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 22px;
    padding-bottom: 16px;
    padding-left: 14px;
    padding-right: 14px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #818CF8;
    background-color: #181B24;
}}

QCheckBox {{
    color: #E2E8F0;
    spacing: 10px;
    font-weight: 500;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 1px solid #3B4254;
    background-color: #12141C;
}}

QCheckBox::indicator:hover {{
    border-color: #6366F1;
    background-color: #1A1D28;
}}

QCheckBox::indicator:checked {{
    background-color: #6366F1;
    border-color: #6366F1;
    image: url('{checkmark_path}');
}}

QPushButton#PrimaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    min-height: 46px;
    padding: 10px 24px;
}}

QPushButton#PrimaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338CA, stop:1 #0891B2);
}}

QPushButton#PrimaryButton:pressed {{
    background: #3730A3;
}}

QPushButton#StopButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    min-height: 46px;
    padding: 10px 24px;
}}

QPushButton#StopButton:hover {{
    background: #B91C1C;
}}

QProgressBar {{
    background-color: #12141C;
    border: 1px solid #2A2F3D;
    border-radius: 8px;
    height: 18px;
    text-align: center;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 600;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #00F2FE);
    border-radius: 7px;
}}

QFrame#StatBox {{
    background-color: #12141C;
    border: 1px solid #232734;
    border-radius: 10px;
    padding: 12px;
}}

QLabel#StatValue {{
    font-size: 20px;
    font-weight: 800;
    color: #38BDF8;
}}

QLabel#StatLabel {{
    font-size: 11px;
    color: #94A3B8;
    font-weight: 500;
}}

QFrame#CountdownBanner {{
    background-color: rgba(99, 102, 241, 0.15);
    border: 1px solid #6366F1;
    border-radius: 10px;
    padding: 14px;
}}

QLabel#CountdownText {{
    font-size: 18px;
    font-weight: 800;
    color: #00F2FE;
}}

QScrollBar:vertical {{
    background-color: #0F1117;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: #2E3446;
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #6366F1;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
    background: none;
}}
"""
