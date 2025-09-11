from PySide6.QtCore import Signal
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import (QVBoxLayout, QComboBox, QLineEdit,
                               QTextEdit, QLabel, QHBoxLayout,
                               QMessageBox, QApplication)
from core.form_dialog import FormDialog
from database.supplierdb.supplier_database import (
    insert_supplier, edit_supplier, supplier_name_exists)


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
        self.mode = mode
        self.conn = conn
        self.supplier_data = supplier_data
        self.parent = parent

        self.setWindowTitle('📦Supplier Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        self.input_type.addItems(
            ['Direct', 'Aggregator', 'White Label', 'Payment Gateway', 'Other']
        )
        self.input_status.addItems(['Active', 'Inactive'])

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

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_cancel)
        self.fields_layout.addLayout(btn_layout)

        # Insert fields layout above buttons
        self.main_layout.insertLayout(0, self.fields_layout)

    def add_supplier(self):
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
