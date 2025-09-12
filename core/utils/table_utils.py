# 1. Standard Library

# 2. Third Party Library
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

# 3. Internal Library


def setup_table_headers(table: QTableWidget, headers: list, stretch_column: str = None):
    """
    Setup QTableWidget headers and resize behavior.

    Args:
        table: The QTableWidget to configure.
        headers: List of column header labels.
        stretch_column: Optional column name to stretch (e.g., 'Description').
    """
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)

    header = table.horizontalHeader()

    # Stretch the chosen column, resize others to contents
    for col, name in enumerate(headers):
        if stretch_column and name == stretch_column:
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            table.setColumnWidth(col, 100)
        else:
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
            table.setColumnWidth(col, 120)


def setup_table_ui(table: QTableWidget, edit_callback):
    # Table columns movable, hides the ID, can't select more than one to edit
    table.horizontalHeader().setSectionsMovable(True)
    table.setColumnHidden(0, True)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    table.cellDoubleClicked.connect(edit_callback)

    # Enable sorting on the table
    table.setSortingEnabled(True)

    # Optional: start with no sort
    table.horizontalHeader().setSortIndicatorShown(True)
    table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)


def filter_table(widget, text):
    text = text.strip().lower()
    filter_col = widget.filter_box.currentIndex() + 1

    for row in range(widget.table.rowCount()):
        item = widget.table.item(row, filter_col)
        if item and text in item.text().lower():
            widget.table.setRowHidden(row, False)
        else:
            widget.table.setRowHidden(row, True if text else False)


def update_table_row(table: QTableWidget, row: int, data: list):
    """
    Update a row in a QTableWidget with given data.

    Args:
        table: The QTableWidget to update.
        row: The row index to update.
        data: List in order.
    """
    # Update table items
    for col_idx, value in enumerate(data):
        table.setItem(row, col_idx, QTableWidgetItem(str(value)))


def add_table_row(table: QTableWidget, data: list):
    """
    Add a new row at the bottom of a QTableWidget.

    Args:
        table: The QTableWidget to update.
        data: Either a list/tuple of values or a dict (values will be used in order).
    """
    # Insert a new row at the bottom
    new_row_index = table.rowCount()
    table.insertRow(new_row_index)

    # Fill the row
    for col_idx, value in enumerate(data):
        table.setItem(new_row_index, col_idx, QTableWidgetItem(str(value)))


def reset_table_order(table: QTableWidget):
    """
    Resets the QTableWidget to the original order.

    Args:
        table (QTableWidget): The table to reset.
    """
    table.setSortingEnabled(True)  # make sure sorting is allowed
    table.sortItems(0, Qt.SortOrder.AscendingOrder)  # sort by first column (ID)


def row_to_dict(table, row, columns):
    """
    Convert a QTableWidget row into a dict using COLUMN_ORDER.
    """
    return {
        col: (table.item(row, idx).text() if table.item(row, idx) else None)
        for idx, col in enumerate(columns)
    }
