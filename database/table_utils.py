# 1. Standard Library

# 2. Third Party Library
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

# 3. Internal Library


def setup_table_ui(table: QTableWidget, edit_callback):
    # Table columns movable, hides the ID, can't select more than one to edit
    table.horizontalHeader().setSectionsMovable(True)
    table.setColumnHidden(0, True)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    table.cellDoubleClicked.connect(edit_callback)


def filter_table(widget, text):
    text = text.strip().lower()
    widget.table.setRowCount(0)

    # Which column to filter on (based on combo box selection)
    # +1 is because first column is id(PK) which is hidden
    filter_col = widget.filter_box.currentIndex() + 1

    for row_data in widget.data:
        value = str(row_data[filter_col]).lower()
        if text in value:
            row_idx = widget.table.rowCount()
            widget.table.insertRow(row_idx)
            for col_idx, col_value in enumerate(row_data):
                widget.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_value)))


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
