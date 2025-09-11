# 1. Standard Library

# 2. Third Party Library
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

# 3. Internal Library


class FormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Form Dialog")

        self.main_layout = QVBoxLayout(self)
        self.btn_add = QPushButton('Accept')
        self.btn_cancel = QPushButton('Cancel')
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(500, 500)
        self.setMaximumSize(500, 16777215)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_cancel)
        self.setup_buttons()

        self.main_layout.addLayout(button_layout)
        self.setLayout(self.main_layout)

    def setup_buttons(self):
        # Standard button wiring
        self.btn_add.clicked.connect(self.accept)  # close with Accepted
        self.btn_cancel.clicked.connect(self.reject)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = FormDialog()
#     window.show()   # now works
#     sys.exit(app.exec())
