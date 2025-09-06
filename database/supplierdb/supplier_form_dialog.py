from PySide6.QtWidgets import QVBoxLayout, QComboBox, QLineEdit, QTextEdit, QLabel, QHBoxLayout
from core.form_dialog import FormDialog
from database.supplierdb.supplier_database import insert_supplier, edit_supplier

class SupplierFormDialog(FormDialog):
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

        self.setWindowTitle('📦Supplier Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        self.input_type.addItems(['Direct', 'Aggregator', 'White Label', 'Payment Gateway', 'Other'])
        self.input_status.addItems(['Active', 'Inactive'])

        # Connect Signals
        if self.mode == 'add':
            self.btn_add.setText('Add Supplier')
            self.btn_add.clicked.connect(self.add_supplier)
        if self.mode == 'edit':
            self.btn_add.setText('Edit Supplier')
            self.btn_add.clicked.connect(self.manage_supplier)

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

        insert_supplier(self.conn, name, contact, supplier_type, status, description)

    def manage_supplier(self):
        supplier_data = {
            'supplier_id': self.supplier_data.get('supplier_id'),
            'supplier_name': self.input_name.text(),
            'supplier_contact': self.input_contact.text(),
            'supplier_type': self.input_type.currentText(),
            'status': self.input_status.currentText(),
            'description': self.input_desc.toPlainText()
        }

        edit_supplier(self.conn, supplier_data)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = SupplierFormDialog()
#     window.show()   # now works
#     sys.exit(app.exec())
