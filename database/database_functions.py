import os
import psycopg2

from dotenv import load_dotenv
from PySide6.QtWidgets import QTableWidgetItem


def get_connection():
    try:
        # TODO: Set up login for database protection
        load_dotenv()
        # DATABASE_URL = os.getenv('DATABASE_URL')
        # conn = psycopg2.connect(DATABASE_URL)
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )
        return conn
    except Exception as e:
        print('Database connection failed:', e)
        return None


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
