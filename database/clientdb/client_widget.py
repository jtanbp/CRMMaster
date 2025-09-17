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
from core import load_data_from_db, remove_entity
from core.utils.table_utils import (
    add_table_row,
    filter_table,
    reset_table_order,
    row_to_dict,
    setup_table_headers,
    setup_table_ui,
    update_table_row,
)
from database.clientdb import ClientFormDialog

# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'client_id',
    'client_name',
    'client_contact',
    'client_type',
    'status',
    'description'
]

HEADERS = [
    'Client ID',
    'Client Name',
    'Contact',
    'Type',
    'Status',
    'Description'
]


class ClientPage(QWidget):
    client_added = Signal(dict)
    client_edited = Signal(dict)

    def __init__(self, parent=None, dev_mode: bool = False, conn=None):
        super().__init__(parent)

        self.refresh_btn = QPushButton('🔄 Refresh')  # Pushbutton Refresh Notification
        self.table = QTableWidget()  # Stores data
        self.filter_box = QComboBox()  # For reference when doing searches
        self.data = {}  # Store data for filtering
        self.table_name = 'client'
        if dev_mode:
            self.table_name += '_dev'
        self.setup_ui()
        self.conn = conn
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Header Row (Label + Buttons)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel('📦Client List'))

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
        add_btn.setToolTip('Add Client')
        add_btn.clicked.connect(self.add_client)
        header_layout.addWidget(add_btn)

        # Remove Button
        remove_btn = QPushButton('➖')
        remove_btn.setToolTip('Remove Client')
        remove_btn.clicked.connect(self.remove_client)
        header_layout.addWidget(remove_btn)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText('Search client...')
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
        setup_table_ui(self.table, self.edit_client)

    # Load Data
    def load_data(self):
        query = f'''
            SELECT {', '.join(COLUMN_ORDER)}
            FROM {self.table_name}
            WHERE deleted_at IS NULL
            ORDER BY {COLUMN_ORDER[0]}
        '''
        self.data = load_data_from_db(
            self.table, self.conn, query, HEADERS, self.refresh_btn
        )

    # Add Client
    def add_client(self):
        dialog = ClientFormDialog(self, 'add', self.table_name, conn=self.conn)
        dialog.client_added.connect(
            lambda data: add_table_row(self.table, [data[key] for key in COLUMN_ORDER])
        )
        dialog.exec()

    # Edit Client
    def edit_client(self, row):
        client_data = row_to_dict(self.table, row, COLUMN_ORDER)
        dialog = ClientFormDialog(
            parent=self, mode='edit', table_name=self.table_name, client_data=client_data, conn=self.conn
        )
        dialog.client_edited.connect(
            lambda data: update_table_row(
                self.table, row, [data[key] for key in COLUMN_ORDER]
            )
        )
        dialog.exec()

    # Remove Client
    def remove_client(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self,
                'Remove Client',
                '⚠️ Please select a client to remove')
            return

        client_id = self.table.item(row, 0).text()
        client_name = self.table.item(row, 1).text()

        confirm = QMessageBox.question(
            self, 'Confirm Delete',
            f'Are you sure you want to delete client: {client_name}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            remove_entity(self.conn, self.table_name, 'client_id', client_id, client_name, 'Client')
            self.table.removeRow(row)
