from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit, QLabel, QHBoxLayout
from core.form_dialog import FormDialog
from database.partnerdb.partner_database import insert_partner, edit_partner

class PartnerFormDialog(FormDialog):
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

        self.setWindowTitle('📦Partner Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        # Connect Signals
        if self.mode == 'add':
            self.btn_add.setText('Add Partner')
            self.btn_add.clicked.connect(self.add_partner)
        if self.mode == 'edit':
            self.btn_add.setText('Edit Partner')
            self.btn_add.clicked.connect(self.manage_partner)

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

        insert_partner(self.conn, name, contact, description)

    def manage_partner(self):
        partner_data = {
            'partner_id': self.partner_data.get('partner_id'),
            'partner_name': self.input_name.text(),
            'partner_contact': self.input_contact.text(),
            'description': self.input_desc.toPlainText()
        }

        edit_partner(self.conn, partner_data)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = PartnerFormDialog()
#     window.show()   # now works
#     sys.exit(app.exec())
