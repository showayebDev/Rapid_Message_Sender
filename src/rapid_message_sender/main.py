import sys
import logging
from PySide6.QtWidgets import QApplication
from rapid_message_sender.ui.window import MainWindow
from rapid_message_sender.ui.icon import get_app_icon

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Rapid Message Sender")
    
    icon = get_app_icon()
    app.setWindowIcon(icon)
    
    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
