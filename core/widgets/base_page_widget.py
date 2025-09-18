# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import Signal, QDate
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget, QDateEdit,
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


class BasePageWidget(QWidget):
    data_added = Signal(dict)
    data_edited = Signal(dict)

    DATE_HEADERS = {'Contract Start', 'Contract End', 'Created At', 'Updated At'}

    def __init__(self, parent=None, dev_mode: bool = False, conn=None,
                 table_name: str = None, column_order=None,
                 headers=None, dialog_class=None, data_name=None):
        super().__init__(parent)

        # Configurable attributes
        self.table_name = table_name + ('_dev' if dev_mode else '')
        self.COLUMN_ORDER = column_order
        self.HEADERS = headers
        self.DialogClass = dialog_class
        self.data_name = data_name

        # UI elements
        self.refresh_btn = QPushButton('🔄 Refresh')
        self.table = QTableWidget()
        self.search_bar = QLineEdit()
        self.date_search = QDateEdit()
        self.filter_box = QComboBox()
        self.data = {}
        self.conn = conn

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f'📦{self.data_name} List'))

        # Refresh button
        self.refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(self.refresh_btn)

        # Reset button
        reset_btn = QPushButton('🔁 Reset Order')
        reset_btn.clicked.connect(lambda: reset_table_order(self.table))
        header_layout.addWidget(reset_btn)

        # Add button
        add_btn = QPushButton('➕')
        add_btn.setToolTip(f'Add {self.data_name}')
        add_btn.clicked.connect(self.add_data)
        header_layout.addWidget(add_btn)

        # Remove button
        remove_btn = QPushButton('➖')
        remove_btn.setToolTip(f'Remove {self.data_name}')
        remove_btn.clicked.connect(self.remove_data)
        header_layout.addWidget(remove_btn)

        # Search bar
        self.search_bar.setPlaceholderText(f'Search {self.data_name.lower()}...')
        self.search_bar.textChanged.connect(lambda text: filter_table(self, text))
        header_layout.addWidget(self.search_bar)

        # Date edit for filtering
        self.date_search.dateChanged.connect(
            lambda date: filter_table(self, date.toString('dd-MM-yyyy'))
        )
        self.date_search.setCalendarPopup(True)
        self.date_search.setDisplayFormat('dd-MM-yyyy')
        self.date_search.hide()  # default hidden
        header_layout.addWidget(self.date_search)

        # Filter box
        self.filter_box.addItems(self.HEADERS[1:])  # exclude ID
        self.filter_box.currentIndexChanged.connect(self.on_filter_column_changed)
        header_layout.addWidget(self.filter_box)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Table
        setup_table_headers(self.table, self.HEADERS, stretch_column='Description')
        setup_table_ui(self.table, self.edit_data)
        layout.addWidget(self.table)

    def on_filter_column_changed(self, index: int):
        """Switch search input depending on column type (date vs text)."""
        selected_header = self.HEADERS[index + 1]  # offset (exclude ID)
        if selected_header in self.DATE_HEADERS:
            self.search_bar.hide()
            self.date_search.setDate(QDate.currentDate())
            self.date_search.show()
            filter_table(self, self.date_search.date().toString('dd-MM-yyyy'))
        else:
            self.date_search.hide()
            self.search_bar.show()
            self.search_bar.clear()  # reset text filter
            filter_table(self, '')

    def load_data(self):
        query = f'''
            SELECT {', '.join(self.COLUMN_ORDER)}
            FROM {self.table_name}
            WHERE deleted_at IS NULL
            ORDER BY {self.COLUMN_ORDER[0]}
        '''
        self.data = load_data_from_db(self.table, self.conn, query, self.HEADERS, self.refresh_btn)

    def add_data(self):
        dialog = self.DialogClass(self, 'add', self.table_name, conn=self.conn)
        dialog.data_added.connect(
            lambda data: add_table_row(self.table, [data[key] for key in self.COLUMN_ORDER])
        )
        dialog.exec()

    def edit_data(self, row):
        data_dict = row_to_dict(self.table, row, self.COLUMN_ORDER)
        dialog = self.DialogClass(
            parent=self, mode='edit', table_name=self.table_name,
            data_dict=data_dict, conn=self.conn
        )
        dialog.data_edited.connect(
            lambda data: update_table_row(self.table, row, [data[key] for key in self.COLUMN_ORDER])
        )
        dialog.exec()

    def remove_data(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, f'Remove {self.data_name}',
                                f'⚠️ Please select a {self.data_name.lower()} to remove')
            return

        data_id = self.table.item(row, 0).text()
        data_name_val = self.table.item(row, 1).text()

        confirm = QMessageBox.question(
            self, 'Confirm Delete',
            f'Are you sure you want to delete {self.data_name.lower()}: {data_name_val}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            remove_entity(self.conn, self.table_name, self.COLUMN_ORDER[0], data_id, data_name_val, self.data_name)
            self.table.removeRow(row)
