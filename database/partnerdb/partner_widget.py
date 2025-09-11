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
from core import (
    add_table_row,
    filter_table,
    reset_table_order,
    setup_table_ui,
    update_refresh_btn,
    update_table_row,
)
from database.partnerdb import PartnerFormDialog, remove_partner

# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'partner_id',
    'partner_name',
    'partner_contact',
    'description'
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
        self.filter_box.addItems(['Partner Name', 'Contact', 'Description'])
        header_layout.addWidget(self.filter_box)

        # Push buttons to the right
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.setup_table()
        layout.addWidget(self.table)

    def setup_table(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            'Partner ID', 'Partner Name', 'Contact', 'Description'
        ])
        # Automatically resize certain columns to fit contents
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # partner Name
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Contact
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )  # Desc can be stretched
        setup_table_ui(self.table, self.edit_partner)

    # Load Data
    def load_data(self):
        if not self.conn:
            QMessageBox.critical(self,
                                 'DB Error',
                                 '❌ Could not connect to database')
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT partner_id, partner_name, partner_contact, description
                    FROM partner
                    WHERE deleted_at IS NULL
                    ORDER BY partner_id;
                """)
                self.data = cur.fetchall()

            # Disable sorting to safely reload rows
            self.table.setSortingEnabled(False)

            self.table.setRowCount(len(self.data))
            for row_idx, row_data in enumerate(self.data):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            # Re-enable sorting after reload
            self.table.setSortingEnabled(True)

            update_refresh_btn(self.refresh_btn, True)
        except Exception as e:
            update_refresh_btn(self.refresh_btn, False)
            QMessageBox.critical(self,
                                 'DB Error',
                                 f"⚠️ Failed to fetch partners:\n{e}")

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
        partner_data = {
            'partner_id': self.table.item(row, 0).text(),  # hidden ID
            'partner_name': self.table.item(row, 1).text(),
            'partner_contact': self.table.item(row, 2).text(),
            'description': self.table.item(row, 3).text()
        }
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
            remove_partner(self.conn, partner_id, partner_name)
            self.table.removeRow(row)
