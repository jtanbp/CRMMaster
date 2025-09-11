from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QMessageBox,
    QHeaderView, QComboBox, QLineEdit
)

from database.database_functions import filter_table
from database.partnerdb.partner_form_dialog import PartnerFormDialog
from database.partnerdb.partner_database import remove_partner


class PartnerPage(QWidget):
    partner_saved = Signal(dict)
    partner_edited = Signal(dict)

    def __init__(self, parent=None, conn=None):
        super().__init__(parent)

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
        refresh_btn = QPushButton('🔄 Refresh')
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        # TODO: Add a status bar at the bottom to give notif

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
        self.table.setColumnHidden(0, True)  # Hide the partner ID
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # partner Name
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Contact

        # Optional: make one column stretch to fill remaining space
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )  # Desc can be stretched

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellDoubleClicked.connect(self.edit_partner)
        header.setSectionsMovable(True)
        # TODO: Set when double click, a partner form dialog for editing appears

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

            self.table.setRowCount(len(self.data))
            for row_idx, row_data in enumerate(self.data):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self,
                                 'DB Error',
                                 f"⚠️ Failed to fetch partners:\n{e}")

    # Add partner
    def add_partner(self):
        dialog = PartnerFormDialog(self, 'add', conn=self.conn)
        # dialog.partner_added.connect(
        # lambda data: self.update_partner_in_table(row, data)
        # )
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
            lambda data: self.update_partner_in_table(row, data)
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

    def update_partner_in_table(self, row, partner_data):
        updated_row = [
            str(partner_data['partner_id']),
            partner_data['partner_name'],
            partner_data['partner_contact'],
            partner_data['description']
        ]
        self.data[row] = updated_row
        for col_idx, value in enumerate(updated_row):
            self.table.setItem(row, col_idx, QTableWidgetItem(value))
