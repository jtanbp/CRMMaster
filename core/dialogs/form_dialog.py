# 1. Standard Library

# 2. Third Party Library
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QMessageBox, QPushButton, QSizePolicy, QVBoxLayout

# 3. Internal Library


class FormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Form Dialog')

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

    def handle_duplicate_name(self, input_widget, entity_label, name, name_exists):
        """
        Reusable duplicate-name handler.

        Returns True if the name is valid (no duplicate),
        False if duplicate found or error occurred.
        """
        if name_exists:
            QMessageBox.warning(
                self, 'Duplicate Name',
                f'A {entity_label.lower()} with the name "{name}" already exists.'
            )
            # highlight in red
            palette = input_widget.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor('#ffcccc'))
            palette.setColor(QPalette.ColorRole.Text, QColor('black'))
            input_widget.setPalette(palette)

            input_widget.setFocus()
            return False

        elif name_exists is None:  # DB error or query failed
            self.accept()
            return False

        # Reset palette back to normal
        input_widget.setPalette(QApplication.palette())
        return True
