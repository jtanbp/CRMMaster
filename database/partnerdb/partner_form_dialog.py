from PySide6.QtCore import Signal
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import (QVBoxLayout, QLineEdit, QTextEdit,
                               QLabel, QHBoxLayout, QMessageBox, QApplication)
from core.form_dialog import FormDialog
from database.partnerdb.partner_database import (
    insert_partner, edit_partner, partner_name_exists)


class PartnerFormDialog(FormDialog):
    partner_added = Signal(dict)
    partner_edited = Signal(dict)

    def __init__(self, parent=None, mode='add', partner_data: dict = None, conn=None):
        super().__init__(parent)

        self.fields_layout = QVBoxLayout()

        # Add partner-specific input fields
        self.input_name = QLineEdit()
        self.input_contact = QLineEdit()
        self.input_desc = QTextEdit()
        self.mode = mode
        self.conn = conn
        self.partner_data = partner_data
        self.parent = parent

        self.setWindowTitle('📦Partner Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        try:
            self.btn_add.clicked.disconnect(self.accept)
        except TypeError:
            # nothing to disconnect (if already removed)
            pass

        # Connect Signals
        if self.mode == 'add':
            self.btn_add.setText('Add Partner')
            self.btn_add.clicked.connect(self.add_partner)
        if self.mode == 'edit':
            self.btn_add.setText('Edit Partner')
            self.btn_add.clicked.connect(self.manage_partner)

        self.input_name.textChanged.connect(self.reset_name_highlight)

    def setup_ui(self):
        # Create a vertical layout for the fields
        partner_name_layout = QHBoxLayout()
        partner_name_layout.addWidget(QLabel('Partner Name:'))
        partner_name_layout.addWidget(self.input_name)

        partner_contact_layout = QHBoxLayout()
        partner_contact_layout.addWidget(QLabel('Partner Contact:'))
        partner_contact_layout.addWidget(self.input_contact)

        partner_desc_layout = QHBoxLayout()
        partner_desc_layout.addWidget(QLabel('Description:'))
        partner_desc_layout.addWidget(self.input_desc)

        if self.mode == 'edit':
            self.input_name.setText(self.partner_data.get('partner_name'))
            self.input_contact.setText(self.partner_data.get('partner_contact'))
            self.input_desc.setText(self.partner_data.get('description'))

        self.fields_layout.addLayout(partner_name_layout)
        self.fields_layout.addLayout(partner_contact_layout)
        self.fields_layout.addLayout(partner_desc_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_cancel)
        self.fields_layout.addLayout(btn_layout)

        # Insert fields layout above buttons
        self.main_layout.insertLayout(0, self.fields_layout)

    def add_partner(self):
        name = self.input_name.text()
        contact = self.input_contact.text()
        description = self.input_desc.toPlainText()

        # 🔎 Check uniqueness
        name_exists = partner_name_exists(self.conn, name)
        if name_exists:
            QMessageBox.warning(
                self,
                'Duplicate Name',
                f"A partner with the name '{name}' already exists."
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

        partner_data = insert_partner(self.conn, name, contact, description)
        self.partner_added.emit(partner_data)
        self.accept()

    def manage_partner(self):
        new_name = self.input_name.text()
        partner_id = self.partner_data.get('partner_id')

        # 🔎 Check uniqueness
        name_exists = partner_name_exists(self.conn, new_name, exclude_id=partner_id)
        if name_exists:
            QMessageBox.warning(
                self,
                'Duplicate Name',
                f"A partner with the name '{new_name}' already exists."
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

        partner_data = {
            'partner_id': self.partner_data.get('partner_id'),
            'partner_name': self.input_name.text(),
            'partner_contact': self.input_contact.text(),
            'description': self.input_desc.toPlainText()
        }

        edit_partner(self.conn, partner_data)
        self.partner_edited.emit(partner_data)
        self.accept()

    def reset_name_highlight(self):
        self.input_name.setPalette(QApplication.palette())
