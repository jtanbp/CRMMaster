from PySide6.QtWidgets import QVBoxLayout, QComboBox, QLineEdit, QTextEdit, QLabel, QHBoxLayout
from core.form_dialog import FormDialog
from database.clientdb.client_database import insert_client, edit_client

class ClientFormDialog(FormDialog):
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

        self.setWindowTitle('📦Client Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        self.input_type.addItems(['Direct', 'Aggregator', 'White Label', 'Payment Gateway', 'Other'])
        self.input_status.addItems(['Active', 'Inactive'])

        # Connect Signals
        if self.mode == 'add':
            self.btn_add.setText('Add Client')
            self.btn_add.clicked.connect(self.add_client)
        if self.mode == 'edit':
            self.btn_add.setText('Edit Client')
            self.btn_add.clicked.connect(self.manage_client)

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
        name = self.input_name.text()
        contact = self.input_contact.text()
        client_type = self.input_type.currentText()
        status = self.input_status.currentText()
        description = self.input_desc.toPlainText()

        insert_client(self.conn, name, contact, client_type, status, description)

    def manage_client(self):
        client_data = {
            'client_id': self.client_data.get('client_id'),
            'client_name': self.input_name.text(),
            'client_contact': self.input_contact.text(),
            'client_type': self.input_type.currentText(),
            'status': self.input_status.currentText(),
            'description': self.input_desc.toPlainText()
        }

        edit_client(self.conn, client_data)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ClientFormDialog()
#     window.show()   # now works
#     sys.exit(app.exec())
