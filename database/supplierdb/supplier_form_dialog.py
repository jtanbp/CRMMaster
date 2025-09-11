# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import Qt, Signal
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
    update_counter,
    validate_characters,
    validate_max_length,
    validate_required,
    validate_selection,
)
from database.supplierdb import edit_supplier, insert_supplier, supplier_name_exists

supplier_types = ['Direct', 'Aggregator', 'White Label', 'Payment Gateway', 'Other']
supplier_status = ['Active', 'Inactive']


class SupplierFormDialog(FormDialog):
    supplier_added = Signal(dict)
    supplier_edited = Signal(dict)

    def __init__(self, parent=None, mode='add', supplier_data: dict = None, conn=None):
        super().__init__(parent)

        self.fields_layout = QVBoxLayout()

        # Add supplier-specific input fields
        self.input_name = QLineEdit()
        self.input_contact = QLineEdit()
        self.input_type = QComboBox()
        self.input_status = QComboBox()
        self.input_desc = QTextEdit()
        self.max_chars = 500
        self.counter_label = QLabel(f"{self.max_chars} characters remaining")
        self.mode = mode
        self.conn = conn
        self.supplier_data = supplier_data
        self.parent = parent

        self.setWindowTitle('📦Supplier Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        self.input_type.addItems(supplier_types)
        self.input_status.addItems(supplier_status)

        try:
            self.btn_add.clicked.disconnect(self.accept)
        except TypeError:
            # nothing to disconnect (if already removed)
            pass

        # Connect Signals
        if self.mode == 'add':
            self.btn_add.setText('Add Supplier')
            self.btn_add.clicked.connect(self.add_supplier)
        if self.mode == 'edit':
            self.btn_add.setText('Edit Supplier')
            self.btn_add.clicked.connect(self.manage_supplier)

        self.input_name.textChanged.connect(self.reset_name_highlight)
        self.input_desc.textChanged.connect(
            lambda: update_counter(self, self.max_chars)
        )

    def setup_ui(self):
        # Create a vertical layout for the fields
        supplier_name_layout = QHBoxLayout()
        supplier_name_layout.addWidget(QLabel('Supplier Name:'))
        supplier_name_layout.addWidget(self.input_name)

        supplier_contact_layout = QHBoxLayout()
        supplier_contact_layout.addWidget(QLabel('Supplier Contact:'))
        supplier_contact_layout.addWidget(self.input_contact)

        supplier_type_layout = QHBoxLayout()
        supplier_type_layout.addWidget(QLabel('Supplier Type:'))
        supplier_type_layout.addWidget(self.input_type)

        supplier_status_layout = QHBoxLayout()
        supplier_status_layout.addWidget(QLabel('Status:'))
        supplier_status_layout.addWidget(self.input_status)

        supplier_desc_layout = QHBoxLayout()
        supplier_desc_layout.addWidget(QLabel('Description:'))
        supplier_desc_layout.addWidget(self.input_desc)

        input_counter_layout = QHBoxLayout()
        input_counter_layout.addWidget(self.counter_label,
                                       alignment=Qt.AlignmentFlag.AlignRight)

        if self.mode == 'edit':
            self.input_name.setText(self.supplier_data.get('supplier_name'))
            self.input_contact.setText(self.supplier_data.get('supplier_contact'))
            self.input_type.setCurrentText(self.supplier_data.get('supplier_type'))
            self.input_status.setCurrentText(self.supplier_data.get('status'))
            self.input_desc.setText(self.supplier_data.get('description'))

        self.fields_layout.addLayout(supplier_name_layout)
        self.fields_layout.addLayout(supplier_contact_layout)
        self.fields_layout.addLayout(supplier_type_layout)
        self.fields_layout.addLayout(supplier_status_layout)
        self.fields_layout.addLayout(supplier_desc_layout)
        self.fields_layout.addLayout(input_counter_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_cancel)
        self.fields_layout.addLayout(btn_layout)

        # Insert fields layout above buttons
        self.main_layout.insertLayout(0, self.fields_layout)

    def add_supplier(self):
        if not self.validate_inputs():
            return

        name = self.input_name.text()
        contact = self.input_contact.text()
        supplier_type = self.input_type.currentText()
        status = self.input_status.currentText()
        description = self.input_desc.toPlainText()

        # 🔎 Check uniqueness
        name_exists = supplier_name_exists(self.conn, name)
        if name_exists:
            QMessageBox.warning(
                self,
                'Duplicate Name',
                f"A supplier with the name '{name}' already exists."
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

        supplier_data = insert_supplier(
            self.conn, name, contact, supplier_type, status, description
        )
        self.supplier_added.emit(supplier_data)
        self.accept()

    def manage_supplier(self):
        if not self.validate_inputs():
            return

        new_name = self.input_name.text()
        supplier_id = self.supplier_data.get('supplier_id')

        # 🔎 Check uniqueness
        name_exist = supplier_name_exists(self.conn, new_name, exclude_id=supplier_id)
        if name_exist:
            QMessageBox.warning(
                self,
                'Duplicate Name',
                f"A supplier with the name '{new_name}' already exists."
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
        elif name_exist is None:
            self.accept()

        # ✅ If OK, reset palette back to normal
        self.input_name.setPalette(QApplication.palette())

        supplier_data = {
            'supplier_id': self.supplier_data.get('supplier_id'),
            'supplier_name': self.input_name.text(),
            'supplier_contact': self.input_contact.text(),
            'supplier_type': self.input_type.currentText(),
            'status': self.input_status.currentText(),
            'description': self.input_desc.toPlainText()
        }

        edit_supplier(self.conn, supplier_data)
        self.supplier_edited.emit(supplier_data)
        self.accept()

    def reset_name_highlight(self):
        self.input_name.setPalette(QApplication.palette())

    def validate_inputs(self) -> bool:
        """Validate all client fields."""
        name = self.input_name.text()
        contact = self.input_contact.text()
        supplier_type = self.input_type.currentText()
        status = self.input_status.currentText()
        description = self.input_desc.toPlainText()

        # Validate name
        if not (validate_required(
                name,
                'Supplier Name',
                self) and
                validate_max_length(
                    name,
                    100,
                    'Supplier Name',
                    self) and
                validate_characters(
                    name,
                    r"[A-Za-z0-9\s]+",
                    'Supplier Name',
                    self)):
            self.input_name.setFocus()
            return False

        # Validate contact (optional)
        if contact:
            if not (validate_max_length(
                    contact,
                    50,
                    'Supplier Contact',
                    self) and
                    validate_characters(
                        contact,
                        r"[A-Za-z0-9\s\+\-\(\)]*",
                        'Supplier Contact',
                        self)):
                self.input_contact.setFocus()
                return False

        # Validate type and status
        if not validate_selection(
                supplier_type,
                supplier_types,
                'Supplier Type',
                self):
            self.input_type.setFocus()
            return False

        if not validate_selection(
                status,
                supplier_status,
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
