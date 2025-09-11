from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QMessageBox,
    QHeaderView, QLineEdit, QComboBox
)

from database.database_functions import filter_table
from database.supplierdb.supplier_form_dialog import SupplierFormDialog
from database.supplierdb.supplier_database import remove_supplier
from database.widget_functions import setup_table_ui, update_table_row, add_table_row


# Define the column order matching your QTableWidget
COLUMN_ORDER = [
    'supplier_id',
    'supplier_name',
    'supplier_contact',
    'supplier_type',
    'status',
    'description'
]


class SupplierPage(QWidget):
    supplier_saved = Signal(dict)
    supplier_edited = Signal(dict)

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
        header_layout.addWidget(QLabel('📦Supplier List'))

        # Refresh Button
        refresh_btn = QPushButton('🔄 Refresh')
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        # TODO: Add a status bar at the bottom to give notif when successful

        # Add Button
        add_btn = QPushButton('➕')
        add_btn.setToolTip('Add Supplier')
        add_btn.clicked.connect(self.add_supplier)
        header_layout.addWidget(add_btn)

        # Remove Button
        remove_btn = QPushButton('➖')
        remove_btn.setToolTip('Remove Supplier')
        remove_btn.clicked.connect(self.remove_supplier)
        header_layout.addWidget(remove_btn)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText('Search supplier...')
        search_bar.textChanged.connect(lambda text: filter_table(self, text))
        header_layout.addWidget(search_bar)

        # Filter Function (By Category, default being name)
        self.filter_box.addItems(
            ['Supplier Name', 'Contact', 'Type', 'Status', 'Description']
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
            'Supplier ID', 'Supplier Name', 'Contact', 'Type', 'Status', 'Description'
        ])
        # Automatically resize certain columns to fit contents
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # Supplier Name
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
        )  # Stretch Desc
        setup_table_ui(self.table, self.edit_supplier)

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
                    "SELECT supplier_id, "
                    "supplier_name, "
                    "supplier_contact, "
                    "supplier_type, "
                    "status, "
                    "description\n"
                    "FROM supplier\n"
                    "WHERE deleted_at IS NULL\n"
                    "ORDER BY supplier_id;")
                self.data = cur.fetchall()

            self.table.setRowCount(len(self.data))
            for row_idx, row_data in enumerate(self.data):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(
                self,
                'DB Error',
                f"⚠️ Failed to fetch suppliers:\n{e}")

    # Add Supplier
    def add_supplier(self):
        dialog = SupplierFormDialog(self, 'add', conn=self.conn)
        dialog.supplier_added.connect(
            lambda data: add_table_row(self.table, [data[key] for key in COLUMN_ORDER])
        )
        dialog.exec()

    # Edit Supplier
    def edit_supplier(self, row):
        # selected row into a dict
        supplier_data = {
            'supplier_id': self.table.item(row, 0).text(),  # hidden ID
            'supplier_name': self.table.item(row, 1).text(),
            'supplier_contact': self.table.item(row, 2).text(),
            'supplier_type': self.table.item(row, 3).text(),
            'status': self.table.item(row, 4).text(),
            'description': self.table.item(row, 5).text()
        }
        dialog = SupplierFormDialog(
            parent=self,
            mode='edit',
            supplier_data=supplier_data,
            conn=self.conn)
        dialog.supplier_edited.connect(
            lambda data: update_table_row(
                self.table, row, [data[key] for key in COLUMN_ORDER]
            )
        )
        dialog.exec()

    # Remove Supplier
    def remove_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Remove Supplier',
                                '⚠️ Please select a supplier to remove')
            return

        supplier_id = self.table.item(row, 0).text()
        supplier_name = self.table.item(row, 1).text()

        confirm = QMessageBox.question(
            self,
            'Confirm Delete',
            f"Are you sure you want to delete supplier: {supplier_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            remove_supplier(self.conn, supplier_id, supplier_name)
            self.table.removeRow(row)

    # def update_supplier_in_table(self, row, supplier_data):
    #     updated_row = [
    #         str(supplier_data['supplier_id']),
    #         supplier_data['supplier_name'],
    #         supplier_data['supplier_contact'],
    #         supplier_data['supplier_type'],
    #         supplier_data['status'],
    #         supplier_data['description']
    #     ]
    #     self.data[row] = updated_row
    #     for col_idx, value in enumerate(updated_row):
    #         self.table.setItem(row, col_idx, QTableWidgetItem(value))
