from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QMessageBox, QInputDialog, QHeaderView
)
from database.database_functions import get_connection
from supplierdb.supplier_form_dialog import SupplierFormDialog
from supplierdb.supplier_database import remove_supplier


class SupplierPage(QWidget):
    def __init__(self, parent=None, conn=None):
        super().__init__(parent)

        self.table = QTableWidget() #Stores data
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
        #TODO: Add a status bar at the bottom to give notifaction when successful or when it fails

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

        # Search Function

        # Filter Function (By Category, default being name)


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
        self.table.setColumnHidden(0, True) # Hide the Supplier ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Supplier Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Contact
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status

        # Optional: make one column stretch to fill remaining space
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Desc can be stretched

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.edit_supplier)
        header.setSectionsMovable(True)
        #TODO: Set when double click, a supplier form dialog for editing appears

    # Load Data
    def load_data(self):
        if not self.conn:
            QMessageBox.critical(self, 'DB Error', '❌ Could not connect to database')
            return

        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT supplier_id, supplier_name, supplier_contact, supplier_type, status, description
                FROM supplier
                WHERE deleted_at IS NULL;
            """)
            rows = cur.fetchall()

            self.table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, 'DB Error', f"⚠️ Failed to fetch suppliers:\n{e}")

    # Add Supplier
    def add_supplier(self):
        dialog = SupplierFormDialog(self, 'add', conn=self.conn)
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
        dialog = SupplierFormDialog(parent=self, mode='edit', supplier_data=supplier_data, conn=self.conn)
        dialog.exec()

    # Remove Supplier
    def remove_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Remove Supplier', '⚠️ Please select a supplier to remove')
            return

        supplier_id = self.table.item(row, 0).text()
        supplier_name = self.table.item(row, 1).text()

        confirm = QMessageBox.question(
            self,
            'Confirm Delete',
            f"Are you sure you want to delete supplier: {supplier_name}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            remove_supplier(self.conn, supplier_id, supplier_name)
            self.table.removeRow(row)
