# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# 3. Internal Library
from core import update_refresh_btn
from database.clientdb import ClientFormDialog, remove_client
from database.table_utils import (
    add_table_row,
    filter_table,
    setup_table_ui,
    update_table_row,
)

# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'client_id',
    'client_name',
    'client_contact',
    'client_type',
    'status',
    'description'
]


class ClientPage(QWidget):
    client_added = Signal(dict)
    client_edited = Signal(dict)

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
        header_layout.addWidget(QLabel('📦Client List'))

        # Refresh Button
        self.refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(self.refresh_btn)

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
        self.filter_box.addItems(
            ['Client Name', 'Contact', 'Type', 'Status', 'Description']
        )
        header_layout.addWidget(self.filter_box)

        # Push buttons to the right
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.setup_table()
        layout.addWidget(self.table)

    def setup_table(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Client ID', 'Client Name', 'Contact', 'Type', 'Status', 'Description'
        ])
        # Automatically resize certain columns to fit contents
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # client Name
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Contact
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # Type
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )  # Status
        header.setSectionResizeMode(
            5, QHeaderView.ResizeMode.Stretch
        )  # Desc can be stretched
        setup_table_ui(self.table, self.edit_client)

    # Load Data
    def load_data(self):
        if not self.conn:
            QMessageBox.critical(self,
                                 'DB Error',
                                 '❌ Could not connect to database')
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT client_id, client_name, client_contact, "
                    "client_type, status, description "
                    "FROM client "
                    "WHERE deleted_at IS NULL "
                    "ORDER BY client_id;"
                )
                self.data = cur.fetchall()

            self.table.setRowCount(len(self.data))
            for row_idx, row_data in enumerate(self.data):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            update_refresh_btn(self.refresh_btn, True)
        except Exception as e:
            update_refresh_btn(self.refresh_btn, False)
            QMessageBox.critical(
                self,
                'DB Error',
                f"⚠️ Failed to fetch clients:\n{e}")

    # Add Client
    def add_client(self):
        dialog = ClientFormDialog(self, 'add', conn=self.conn)
        dialog.client_added.connect(
            lambda data: add_table_row(self.table, [data[key] for key in COLUMN_ORDER])
        )
        dialog.exec()

    # Edit Client
    def edit_client(self, row):
        # selected row into a dict
        client_data = {
            'client_id': self.table.item(row, 0).text(),  # hidden ID
            'client_name': self.table.item(row, 1).text(),
            'client_contact': self.table.item(row, 2).text(),
            'client_type': self.table.item(row, 3).text(),
            'status': self.table.item(row, 4).text(),
            'description': self.table.item(row, 5).text()
        }
        dialog = ClientFormDialog(
            parent=self, mode='edit', client_data=client_data, conn=self.conn
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
            self,
            'Confirm Delete',
            f"Are you sure you want to delete client: {client_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            remove_client(self.conn, client_id, client_name)
            self.table.removeRow(row)
