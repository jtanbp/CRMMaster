# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
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
    edit_entity,
    entity_name_exists,
    insert_entity,
    update_counter,
    validate_characters,
    validate_max_length,
    validate_required,
    validate_selection,
)

supplier_types = ['Direct', 'Aggregator', 'White Label', 'Payment Gateway', 'Other']
supplier_status = ['Active', 'Inactive']


class SupplierFormDialog(FormDialog):
    data_added = Signal(dict)  # Required to update in base page widget
    data_edited = Signal(dict)  # Required to update in base page widget

    def __init__(self, parent=None, mode='add', table_name='supplier', data_dict: dict = None, conn=None):
        super().__init__(parent)

        self.fields_layout = QVBoxLayout()

        # Add supplier-specific input fields
        self.input_name = QLineEdit()
        self.input_contact = QLineEdit()
        self.input_type = QComboBox()
        self.input_status = QComboBox()
        self.input_desc = QTextEdit()
        self.input_start_date = QDateEdit()
        self.input_end_date = QDateEdit()
        self.start_checkbox = QCheckBox()
        self.end_checkbox = QCheckBox()
        self.max_chars = 500
        self.counter_label = QLabel(f'{self.max_chars} characters remaining')
        self.table_name = table_name
        self.mode = mode
        self.conn = conn
        self.supplier_data = data_dict
        self.parent = parent

        self.setWindowTitle('📦Supplier Form')
        self.setup()
        self.setup_ui()

    def setup(self):
        self.input_type.addItems(supplier_types)
        self.input_status.addItems(supplier_status)

        # Contract Start Date
        self.input_start_date.setCalendarPopup(True)
        self.input_start_date.setDisplayFormat('dd-MM-yyyy')
        self.input_start_date.setDate(QDate.currentDate())  # empty date
        self.input_start_date.setEnabled(False)

        # Contract End Date
        self.input_end_date.setCalendarPopup(True)
        self.input_end_date.setDisplayFormat('dd-MM-yyyy')
        self.input_end_date.setDate(QDate.currentDate())
        self.input_end_date.setEnabled(False)

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
        # Connect checkbox to enable/disable the date field
        self.start_checkbox.stateChanged.connect(
            lambda state: self.input_start_date.setEnabled(state == 2)  # 2 = checked
        )
        self.end_checkbox.stateChanged.connect(
            lambda state: self.input_end_date.setEnabled(state == 2)
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
        input_counter_layout.addWidget(self.counter_label, alignment=Qt.AlignmentFlag.AlignRight)

        contract_dates_layout = QHBoxLayout()

        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel('Start Date:'))
        start_layout.addWidget(self.start_checkbox)
        start_layout.addWidget(self.input_start_date)

        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel('End Date:'))
        end_layout.addWidget(self.end_checkbox)
        end_layout.addWidget(self.input_end_date)

        # Add both layouts to main horizontal layout with equal stretch
        contract_dates_layout.addLayout(start_layout, 1)
        contract_dates_layout.addLayout(end_layout, 1)

        if self.mode == 'edit':
            self.input_name.setText(self.supplier_data.get('supplier_name'))
            self.input_contact.setText(self.supplier_data.get('supplier_contact'))
            self.input_type.setCurrentText(self.supplier_data.get('supplier_type'))
            self.input_status.setCurrentText(self.supplier_data.get('status'))
            self.input_desc.setText(self.supplier_data.get('description'))

            # Handle start date
            contract_start = self.supplier_data.get('contract_start')
            if contract_start and contract_start != 'None':
                year, month, day = map(int, contract_start.split('-'))
                self.input_start_date.setDate(QDate(year, month, day))
                self.start_checkbox.setChecked(True)
                self.input_start_date.setEnabled(True)
            else:
                self.start_checkbox.setChecked(False)
                self.input_start_date.setEnabled(False)

            # Handle end date
            contract_end = self.supplier_data.get('contract_end')
            if contract_end and contract_end != 'None':
                year, month, day = map(int, contract_end.split('-'))
                self.input_end_date.setDate(QDate(year, month, day))
                self.end_checkbox.setChecked(True)
                self.input_end_date.setEnabled(True)
            else:
                self.end_checkbox.setChecked(False)
                self.input_end_date.setEnabled(False)

        self.fields_layout.addLayout(supplier_name_layout)
        self.fields_layout.addLayout(supplier_contact_layout)
        self.fields_layout.addLayout(supplier_type_layout)
        self.fields_layout.addLayout(supplier_status_layout)
        self.fields_layout.addLayout(supplier_desc_layout)
        self.fields_layout.addLayout(input_counter_layout)
        self.fields_layout.addLayout(contract_dates_layout)

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
        name_exist = entity_name_exists(self.conn, self.table_name, 'supplier_name', name)

        if not self.handle_duplicate_name(self.input_name, 'Supplier', name, name_exist):
            return

        # Handle dates (optional)
        contract_start = (
            self.input_start_date.date().toString('yyyy-MM-dd')
            if self.start_checkbox.isChecked()
            else None
        )
        contract_end = (
            self.input_end_date.date().toString('yyyy-MM-dd')
            if self.end_checkbox.isChecked()
            else None
        )

        data = {
            'supplier_name': name,
            'supplier_contact': contact,
            'supplier_type': supplier_type,
            'supplier_status': status,
            'description': description,
            'contract_start': contract_start,
            'contract_end': contract_end,
        }
        supplier_data = insert_entity(self.conn, self.table_name, data, 'supplier_id', 'Supplier')
        self.data_added.emit(supplier_data)
        self.accept()

    def manage_supplier(self):
        if not self.validate_inputs():
            return

        new_name = self.input_name.text()
        supplier_id = self.supplier_data.get('supplier_id')

        # 🔎 Check uniqueness
        name_exist = entity_name_exists(self.conn, self.table_name, 'supplier_name',
                                        new_name, 'supplier_id', exclude_id=supplier_id)
        if not self.handle_duplicate_name(self.input_name, 'Supplier', new_name, name_exist):
            return
        elif name_exist is None:
            self.accept()

        # ✅ If OK, reset palette back to normal
        self.input_name.setPalette(QApplication.palette())

        # Handle dates (optional)
        contract_start = (
            self.input_start_date.date().toString('yyyy-MM-dd')
            if self.start_checkbox.isChecked()
            else None
        )
        contract_end = (
            self.input_end_date.date().toString('yyyy-MM-dd')
            if self.end_checkbox.isChecked()
            else None
        )

        supplier_data = {
            'supplier_id': supplier_id,
            'supplier_name': self.input_name.text(),
            'supplier_contact': self.input_contact.text(),
            'supplier_type': self.input_type.currentText(),
            'supplier_status': self.input_status.currentText(),
            'description': self.input_desc.toPlainText(),
            'contract_start': contract_start,
            'contract_end': contract_end,
        }

        supplier_data = edit_entity(self.conn, self.table_name,
                                    'supplier_id', supplier_data, 'Supplier')
        self.data_edited.emit(supplier_data)
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
        if not (validate_required(name, 'Supplier Name', self) and
                validate_max_length(name, 100, 'Supplier Name', self) and
                validate_characters(name, r'[A-Za-z0-9\s]+', 'Supplier Name', self)):
            self.input_name.setFocus()
            return False

        # Validate contact (optional)
        if contact:
            if not (validate_max_length(contact, 50, 'Supplier Contact', self) and
                    validate_characters(contact, r'[A-Za-z0-9\s\+\-\(\)]*',
                                        'Supplier Contact', self)):
                self.input_contact.setFocus()
                return False

        # Validate type and status
        if not validate_selection(supplier_type, supplier_types, 'Supplier Type', self):
            self.input_type.setFocus()
            return False

        if not validate_selection(status, supplier_status, 'Status', self):
            self.input_status.setFocus()
            return False

        # Validate description (optional)
        if (description and
                not validate_max_length(description, 500, 'Description', self)):
            self.input_desc.setFocus()
            return False

        # --- Validate contract dates (optional) ---
        # Start date
        if self.start_checkbox.isChecked():
            if not self.input_start_date.date().isValid():
                self.input_start_date.setFocus()
                QMessageBox.warning(self, 'Invalid Date', 'Please enter a valid Start Date.')
                return False

        # End date
        if self.end_checkbox.isChecked():
            if not self.input_end_date.date().isValid():
                self.input_end_date.setFocus()
                QMessageBox.warning(self, 'Invalid Date', 'Please enter a valid End Date.')
                return False

        # Optional: ensure start <= end
        if self.start_checkbox.isChecked() and self.end_checkbox.isChecked():
            if self.input_start_date.date() > self.input_end_date.date():
                self.input_start_date.setFocus()
                QMessageBox.warning(self, 'Invalid Dates', 'Start Date cannot be after End Date.')
                return False

        return True
