# 1. Standard Library

# 2. Third Party Library
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

# 3. Internal Library


def load_data_from_db(widget, conn, query, headers, refresh_btn=None):
    """
    Generic DB loader for QTableWidget.

    Args:
        widget: QTableWidget to populate.
        conn: psycopg2 or other DB connection.
        query: SQL query string to run.
        headers: list of header labels for the table.
        refresh_btn: optional QPushButton to update with status.
    """
    if not conn:
        QMessageBox.critical(
            widget,
            'DB Error',
            '❌ Could not connect to database')
        return []

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            data = cur.fetchall()

        # Disable sorting to safely reload rows
        widget.setSortingEnabled(False)

        # Set headers
        widget.setColumnCount(len(headers))
        widget.setHorizontalHeaderLabels(headers)

        # Fill rows
        widget.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        # Re-enable sorting
        widget.setSortingEnabled(True)

        if refresh_btn:
            from core import update_refresh_btn
            update_refresh_btn(refresh_btn, True)

        return data
    except Exception as e:
        if refresh_btn:
            from core import update_refresh_btn
            update_refresh_btn(refresh_btn, False)

        QMessageBox.critical(
            widget,
            'DB Error',
            f'⚠️ Failed to fetch data:\n{e}')
        return []


def insert_entity(conn, table, data, id_column, display_name):
    """
    Generic insert function.
    - table: name of the table ('supplier' or 'client')
    - data: dict of column_name: value (excluding ID)
    - id_column: primary key column (e.g. 'supplier_id')
    - display_name: human readable name ('Supplier' / 'Client')
    """
    if not conn:
        QMessageBox.critical(None, 'DB Error''❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            sql = (
                f'INSERT INTO {table} ({columns}) '
                f'VALUES ({placeholders}) RETURNING {id_column};'
            )
            cur.execute(sql, tuple(data.values()))
            new_id = cur.fetchone()[0]

        entity_data = {id_column: new_id, **data}

        conn.commit()
        QMessageBox.information(None, 'Success', f'✅ {display_name} added')
        return entity_data
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None, 'DB Error', f'⚠️ Failed to add {display_name.lower()}:\n{e}')


def remove_entity(conn, table, id_column, entity_id, name_value, display_name):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                f'''
                UPDATE {table}
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE {id_column} = %s
                ''',
                (entity_id,),
            )
        conn.commit()
        QMessageBox.information(None, 'Deleted', f'❌ {display_name} "{name_value}" removed')
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None, 'DB Error', f'⚠️ Failed to delete {display_name.lower()}:\n{e}')


def edit_entity(conn, table, id_column, entity_data, display_name):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        entity_id = entity_data.get(id_column)
        update_fields = [f'{col} = %s' for col in entity_data if col != id_column]
        sql = (
            f'UPDATE {table} '
            f'SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP '
            f'WHERE {id_column} = %s'
        )

        values = [entity_data[col] for col in entity_data if col != id_column]
        values.append(entity_id)

        with conn.cursor() as cur:
            cur.execute(sql, tuple(values))
        conn.commit()

        QMessageBox.information(None, 'Edited', f'🔄 {display_name} edited')
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None, 'DB Error', f'⚠️ Failed to edit {display_name.lower()}:\n{e}')


def entity_name_exists(
        conn, table, name_column, name_value, id_column=None, exclude_id=None):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    with conn.cursor() as cur:
        if exclude_id:
            cur.execute(
                f'''
                SELECT 1 FROM {table}
                WHERE {name_column} = %s
                  AND {id_column} <> %s
                  AND deleted_at IS NULL
                ''',
                (name_value, exclude_id),
            )
        else:
            cur.execute(
                f'''
                SELECT 1 FROM {table}
                WHERE {name_column} = %s
                  AND deleted_at IS NULL
                ''',
                (name_value,),
            )
        return cur.fetchone() is not None
