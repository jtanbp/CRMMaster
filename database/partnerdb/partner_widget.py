# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

# 3. Internal Library
from core import (
    add_table_row,
    filter_table,
    load_data_from_db,
    remove_entity,
    reset_table_order,
    row_to_dict,
    setup_table_headers,
    setup_table_ui,
    update_table_row,
)
from database.partnerdb import PartnerFormDialog

# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'partner_id',
    'partner_name',
    'partner_contact',
    'description'
]

HEADERS = [
    'Partner ID',
    'Partner Name',
    'Contact',
    'Description'
]


class PartnerPage(QWidget):
    partner_saved = Signal(dict)
    partner_edited = Signal(dict)

    def __init__(self, parent=None, conn=None):
        super().__init__(parent)

        self.refresh_btn = QPushButton('🔄 Refresh')  # Pushbutton Refresh Notification
        self.table = QTableWidget()  # Stores data
        self.filter_box = QComboBox()  # For reference when doing searches
        self.data = {}  # Store data for filtering
        self.setup_ui()
        self.conn = conn
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Header Row (Label + Buttons)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel('📦Partner List'))

        # Refresh Button
        self.refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(self.refresh_btn)

        # Reset Table Button
        reset_btn = QPushButton('🔁 Reset Order')
        reset_btn.clicked.connect(
            lambda: reset_table_order(self.table)
        )
        header_layout.addWidget(reset_btn)

        # Add Button
        add_btn = QPushButton('➕')
        add_btn.setToolTip('Add Partner')
        add_btn.clicked.connect(self.add_partner)
        header_layout.addWidget(add_btn)

        # Remove Button
        remove_btn = QPushButton('➖')
        remove_btn.setToolTip('Remove Partner')
        remove_btn.clicked.connect(self.remove_partner)
        header_layout.addWidget(remove_btn)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText('Search partner...')
        search_bar.textChanged.connect(lambda text: filter_table(self, text))
        header_layout.addWidget(search_bar)

        # Filter Function (By Category, default being name)
        self.filter_box.addItems(HEADERS[1:])  # [1:] exclude id column
        header_layout.addWidget(self.filter_box)

        # Push buttons to the right
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.setup_table()
        layout.addWidget(self.table)

    def setup_table(self):
        setup_table_headers(self.table, HEADERS, stretch_column='Description')
        setup_table_ui(self.table, self.edit_partner)

    # Load Data
    def load_data(self):
        query = f"""
            SELECT {', '.join(COLUMN_ORDER)}
            FROM partner
            WHERE deleted_at IS NULL
            ORDER BY {COLUMN_ORDER[0]}
        """
        self.data = load_data_from_db(
            self.table, self.conn, query, HEADERS, self.refresh_btn
        )

    # Add partner
    def add_partner(self):
        dialog = PartnerFormDialog(self, 'add', conn=self.conn)
        dialog.partner_added.connect(
            lambda data: add_table_row(self.table, [data[key] for key in COLUMN_ORDER])
        )
        dialog.exec()

    # Edit partner
    def edit_partner(self, row):
        # selected row into a dict
        partner_data = row_to_dict(self.table, row, COLUMN_ORDER)
        dialog = PartnerFormDialog(
            parent=self, mode='edit', partner_data=partner_data, conn=self.conn
        )
        dialog.partner_edited.connect(
            lambda data: update_table_row(
                self.table, row, [data[key] for key in COLUMN_ORDER]
            )
        )
        dialog.exec()

    # Remove partner
    def remove_partner(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self,
                                'Remove Partner',
                                '⚠️ Please select a partner to remove')
            return

        partner_id = self.table.item(row, 0).text()
        partner_name = self.table.item(row, 1).text()

        confirm = QMessageBox.question(
            self,
            'Confirm Delete',
            f"Are you sure you want to delete partner: {partner_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            remove_entity(
                self.conn,
                'partner',
                'partner_id',
                partner_id,
                partner_name,
                'Partner')
            self.table.removeRow(row)
