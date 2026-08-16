import os
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QPen, QColor, QLinearGradient, QIcon
from PySide6.QtCore import Qt

def render_icon_pixmap(size: int = 512) -> QPixmap:
    """Renders a high-resolution vector pixmap matching the app icon design."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    padding = max(1.0, size * 0.04)
    rect_size = size - (padding * 2)

    # Rounded background card
    bg_grad = QLinearGradient(0, 0, size, size)
    bg_grad.setColorAt(0.0, QColor("#1E1B4B"))
    bg_grad.setColorAt(1.0, QColor("#0F172A"))
    painter.setBrush(bg_grad)

    border_pen = QPen()
    border_pen.setWidthF(max(1.0, size * 0.04))
    border_pen.setColor(QColor("#6366F1"))
    painter.setPen(border_pen)

    r = size * 0.22
    painter.drawRoundedRect(padding, padding, rect_size, rect_size, r, r)

    # Chat Bubble Shape
    bubble_path = QPainterPath()
    bx, by, bw, bh = size * 0.18, size * 0.20, size * 0.64, size * 0.48
    bubble_path.addRoundedRect(bx, by, bw, bh, size * 0.12, size * 0.12)

    # Tail
    bubble_path.moveTo(size * 0.35, by + bh)
    bubble_path.lineTo(size * 0.25, size * 0.78)
    bubble_path.lineTo(size * 0.46, by + bh)

    bubble_grad = QLinearGradient(0, size * 0.2, size, size * 0.8)
    bubble_grad.setColorAt(0.0, QColor("#4F46E5"))
    bubble_grad.setColorAt(1.0, QColor("#06B6D4"))

    painter.setBrush(bubble_grad)
    painter.setPen(Qt.NoPen)
    painter.drawPath(bubble_path)

    # Lightning Bolt Symbol ⚡
    bolt_path = QPainterPath()
    s = size
    bolt_path.moveTo(s * 0.54, s * 0.25)
    bolt_path.lineTo(s * 0.38, s * 0.50)
    bolt_path.lineTo(s * 0.50, s * 0.50)
    bolt_path.lineTo(s * 0.42, s * 0.75)
    bolt_path.lineTo(s * 0.62, s * 0.45)
    bolt_path.lineTo(s * 0.50, s * 0.45)
    bolt_path.closeSubpath()

    painter.setBrush(QColor("#00F2FE"))
    painter.drawPath(bolt_path)

    painter.end()
    return pix

def generate_thumbnail(size: int = 512) -> str:
    """
    Renders and saves a 512px x 512px square thumbnail PNG.
    """
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    thumbnail_path = os.path.join(assets_dir, "app_thumbnail_512.png")
    
    # Project root path for easy user access
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    root_thumbnail_path = os.path.join(root_dir, "app_thumbnail_512.png")

    pix = render_icon_pixmap(size)
    pix.save(thumbnail_path, "PNG")
    try:
        pix.save(root_thumbnail_path, "PNG")
    except Exception:
        pass

    return thumbnail_path

def get_app_icon() -> QIcon:
    """
    Generates and returns the multi-resolution application icon.
    Ensures assets/app_icon.png and assets/app_icon.ico are available.
    """
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    icon_png_path = os.path.join(assets_dir, "app_icon.png")
    icon_ico_path = os.path.join(assets_dir, "app_icon.ico")

    # Ensure 512px thumbnail exists
    generate_thumbnail(512)

    # If ICO file exists, load directly for native OS icon support
    if os.path.exists(icon_ico_path):
        icon = QIcon(icon_ico_path)
        if not icon.isNull():
            return icon

    icon = QIcon()
    sizes = [16, 24, 32, 48, 64, 128, 256, 512]

    for size in sizes:
        pix = render_icon_pixmap(size)
        icon.addPixmap(pix)

        if size == 256 and not os.path.exists(icon_png_path):
            pix.save(icon_png_path, "PNG")

    return icon
