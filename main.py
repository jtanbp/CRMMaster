# 1. Standard Library
import sys

# 2. Third Party Library
from PySide6.QtWidgets import QApplication

# 3. Internal Library
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
