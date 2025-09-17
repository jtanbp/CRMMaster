# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QVBoxLayout

# 3. Internal Library
from core import (
    FormDialog,
    edit_entity,
    entity_name_exists,
    insert_entity,
    update_counter,
    validate_characters,
    validate_max_length,
    validate_required,
)


class PartnerFormDialog(FormDialog):
    partner_added = Signal(dict)
    partner_edited = Signal(dict)

    def __init__(self, parent=None, mode='add', table_name='partner', partner_data: dict = None, conn=None):
        super().__init__(parent)

        self.fields_layout = QVBoxLayout()

        # Add partner-specific input fields
        self.input_name = QLineEdit()
        self.input_contact = QLineEdit()
        self.input_desc = QTextEdit()
        self.max_chars = 500
        self.counter_label = QLabel(f'{self.max_chars} characters remaining')
        self.table_name = table_name
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
        self.input_desc.textChanged.connect(
            lambda: update_counter(self, self.max_chars)
        )

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

        input_counter_layout = QHBoxLayout()
        input_counter_layout.addWidget(self.counter_label, alignment=Qt.AlignmentFlag.AlignRight)

        if self.mode == 'edit':
            self.input_name.setText(self.partner_data.get('partner_name'))
            self.input_contact.setText(self.partner_data.get('partner_contact'))
            self.input_desc.setText(self.partner_data.get('description'))

        self.fields_layout.addLayout(partner_name_layout)
        self.fields_layout.addLayout(partner_contact_layout)
        self.fields_layout.addLayout(partner_desc_layout)
        self.fields_layout.addLayout(input_counter_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_cancel)
        self.fields_layout.addLayout(btn_layout)

        # Insert fields layout above buttons
        self.main_layout.insertLayout(0, self.fields_layout)

    def add_partner(self):
        if not self.validate_inputs():
            return

        name = self.input_name.text()
        contact = self.input_contact.text()
        description = self.input_desc.toPlainText()

        # 🔎 Check uniqueness
        name_exist = entity_name_exists(self.conn, self.table_name, 'partner_name', name)
        if not self.handle_duplicate_name(self.input_name, 'Partner', name, name_exist):
            return

        data = {
            'partner_name': name,
            'partner_contact': contact,
            'description': description,
        }
        partner_data = insert_entity(self.conn, self.table_name, data, 'partner_id', 'Partner')
        self.partner_added.emit(partner_data)
        self.accept()

    def manage_partner(self):
        if not self.validate_inputs():
            return

        new_name = self.input_name.text()
        partner_id = self.partner_data.get('partner_id')

        # 🔎 Check uniqueness
        name_exist = entity_name_exists(self.conn, self.table_name, 'partner_name',
                                        new_name, 'partner_id', exclude_id=partner_id)
        if not self.handle_duplicate_name(self.input_name, 'Partner', new_name, name_exist):
            return

        partner_data = {
            'partner_id': self.partner_data.get('partner_id'),
            'partner_name': self.input_name.text(),
            'partner_contact': self.input_contact.text(),
            'description': self.input_desc.toPlainText()
        }

        edit_entity(self.conn, self.table_name, 'partner_id', partner_data, 'Partner')
        self.partner_edited.emit(partner_data)
        self.accept()

    def reset_name_highlight(self):
        self.input_name.setPalette(QApplication.palette())

    def validate_inputs(self) -> bool:
        """Validate all client fields."""
        name = self.input_name.text()
        contact = self.input_contact.text()
        description = self.input_desc.toPlainText()

        # Validate name
        if not (validate_required(name, 'Partner Name', self) and
                validate_max_length(name, 100, 'Partner Name', self) and
                validate_characters(name, r'[A-Za-z0-9\s]+', 'Partner Name', self)):
            self.input_name.setFocus()
            return False

        # Validate contact (optional)
        if contact:
            if not (validate_max_length(contact, 50, 'Partner Contact', self) and
                    validate_characters(contact, r'[A-Za-z0-9\s\+\-\(\)]*',
                                        'Partner Contact', self)):
                self.input_contact.setFocus()
                return False

        # Validate description (optional)
        if (description and
                not validate_max_length(description, 500, 'Description', self)):
            self.input_desc.setFocus()
            return False

        return True
