# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

# 3. Internal Library
from core import (
    FormDialog,
    validate_characters,
    validate_max_length,
    validate_required,
    validate_selection,
)
from database.clientdb import client_name_exists, edit_client, insert_client

client_types = ['VIP', 'Client']
client_status = ['Active', 'Inactive']


class ClientFormDialog(FormDialog):
    client_added = Signal(dict)
    client_edited = Signal(dict)

    def __init__(self, parent=None, mode='add', client_data: dict = None, conn=None):
        super().__init__(parent)

        self.fields_layout = QVBoxLayout()

        # Add client-specific input fields
        self.input_name = QLineEdit()
        self.input_contact = QLineEdit()
        self.input_type = QComboBox()
        self.input_status = QComboBox()
        self.input_desc = QTextEdit()
        self.mode = mode
        self.conn = conn
        self.client_data = client_data
        self.parent = parent

        self.setWindowTitle('📦Client Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        self.input_type.addItems(client_types)
        self.input_status.addItems(client_status)

        try:
            self.btn_add.clicked.disconnect(self.accept)
        except TypeError:
            # nothing to disconnect (if already removed)
            pass

        # Connect Signals
        if self.mode == 'add':
            self.btn_add.setText('Add Client')
            self.btn_add.clicked.connect(self.add_client)
        if self.mode == 'edit':
            self.btn_add.setText('Edit Client')
            self.btn_add.clicked.connect(self.manage_client)

        self.input_name.textChanged.connect(self.reset_name_highlight)

    def setup_ui(self):
        # Create a vertical layout for the fields
        client_name_layout = QHBoxLayout()
        client_name_layout.addWidget(QLabel('Client Name:'))
        client_name_layout.addWidget(self.input_name)

        client_contact_layout = QHBoxLayout()
        client_contact_layout.addWidget(QLabel('Client Contact:'))
        client_contact_layout.addWidget(self.input_contact)

        client_type_layout = QHBoxLayout()
        client_type_layout.addWidget(QLabel('Client Type:'))
        client_type_layout.addWidget(self.input_type)

        client_status_layout = QHBoxLayout()
        client_status_layout.addWidget(QLabel('Status:'))
        client_status_layout.addWidget(self.input_status)

        client_desc_layout = QHBoxLayout()
        client_desc_layout.addWidget(QLabel('Description:'))
        client_desc_layout.addWidget(self.input_desc)

        if self.mode == 'edit':
            self.input_name.setText(self.client_data.get('client_name'))
            self.input_contact.setText(self.client_data.get('client_contact'))
            self.input_type.setCurrentText(self.client_data.get('client_type'))
            self.input_status.setCurrentText(self.client_data.get('status'))
            self.input_desc.setText(self.client_data.get('description'))

        self.fields_layout.addLayout(client_name_layout)
        self.fields_layout.addLayout(client_contact_layout)
        self.fields_layout.addLayout(client_type_layout)
        self.fields_layout.addLayout(client_status_layout)
        self.fields_layout.addLayout(client_desc_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_cancel)
        self.fields_layout.addLayout(btn_layout)

        # Insert fields layout above buttons
        self.main_layout.insertLayout(0, self.fields_layout)

    def add_client(self):
        if not self.validate_inputs():
            return

        name = self.input_name.text()
        contact = self.input_contact.text()
        client_type = self.input_type.currentText()
        status = self.input_status.currentText()
        description = self.input_desc.toPlainText()

        # 🔎 Check uniqueness
        name_exists = client_name_exists(self.conn, name)
        if name_exists:
            QMessageBox.warning(
                self,
                'Duplicate Name',
                f"A client with the name '{name}' already exists."
            )
            # ✅ highlight the name field in red
            palette = self.input_name.palette()
            palette.setColor(
                QPalette.ColorRole.Base, QColor('#ffcccc')
            )  # light red background
            palette.setColor(
                QPalette.ColorRole.Text, QColor('black')
            )  # text color
            self.input_name.setPalette(palette)

            self.input_name.setFocus()  # put cursor back in the field
            return  # stop saving
        elif name_exists is None:
            self.accept()

        # ✅ If OK, reset palette back to normal
        self.input_name.setPalette(QApplication.palette())

        client_data = insert_client(
            self.conn, name, contact, client_type, status, description
        )
        self.client_added.emit(client_data)
        self.accept()

    def manage_client(self):
        if not self.validate_inputs():
            return

        new_name = self.input_name.text()
        client_id = self.client_data.get('client_id')

        # 🔎 Check uniqueness
        name_exists = client_name_exists(self.conn, new_name, exclude_id=client_id)
        if name_exists:
            QMessageBox.warning(
                self,
                'Duplicate Name',
                f"A client with the name '{new_name}' already exists."
            )
            # ✅ highlight the name field in red
            palette = self.input_name.palette()
            palette.setColor(
                QPalette.ColorRole.Base, QColor('#ffcccc')
            )  # light red background
            palette.setColor(
                QPalette.ColorRole.Text, QColor('black')
            )  # text color
            self.input_name.setPalette(palette)

            self.input_name.setFocus()  # put cursor back in the field
            return  # stop saving
        elif name_exists is None:
            self.accept()

        # ✅ If OK, reset palette back to normal
        self.input_name.setPalette(QApplication.palette())

        client_data = {
            'client_id': self.client_data.get('client_id'),
            'client_name': self.input_name.text(),
            'client_contact': self.input_contact.text(),
            'client_type': self.input_type.currentText(),
            'status': self.input_status.currentText(),
            'description': self.input_desc.toPlainText()
        }

        edit_client(self.conn, client_data)
        self.client_edited.emit(client_data)
        self.accept()

    def reset_name_highlight(self):
        self.input_name.setPalette(QApplication.palette())

    def validate_inputs(self) -> bool:
        """Validate all client fields."""
        name = self.input_name.text()
        contact = self.input_contact.text()
        client_type = self.input_type.currentText()
        status = self.input_status.currentText()
        description = self.input_desc.toPlainText()

        # Validate name
        if not (validate_required(
                name,
                'Client Name',
                self) and
                validate_max_length(
                    name,
                    100,
                    'Client Name',
                    self) and
                validate_characters(
                    name,
                    r"[A-Za-z0-9\s]+",
                    'Client Name',
                    self)):
            self.input_name.setFocus()
            return False

        # Validate contact (optional)
        if contact:
            if not (validate_max_length(
                    contact,
                    50,
                    'Client Contact',
                    self) and
                    validate_characters(
                        contact,
                        r"[A-Za-z0-9\s\+\-\(\)]*",
                        'Client Contact',
                        self)):
                self.input_contact.setFocus()
                return False

        # Validate type and status
        if not validate_selection(
                client_type,
                client_types,
                'Client Type',
                self):
            self.input_type.setFocus()
            return False

        if not validate_selection(
                status,
                client_status,
                'Status',
                self):
            self.input_status.setFocus()
            return False

        # Validate description (optional)
        if (description and
                not validate_max_length(description, 500, 'Description', self)):
            self.input_desc.setFocus()
            return False

        return True
