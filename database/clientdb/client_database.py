# 1. Standard Library

# 2. Third Party Library
from PySide6.QtWidgets import QMessageBox

# 3. Internal Library


def insert_client(conn, client_name, client_contact, client_type, status, description):
    if not conn:
        QMessageBox.critical(None,
                             'DB Error',
                             '❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO client ("
                "client_name, "
                "client_contact, "
                "client_type, "
                "status, "
                "description"
                ") VALUES (%s, %s, %s, %s, %s) "
                "RETURNING client_id;"
            )

            cur.execute(sql,
                        (client_name, client_contact, client_type, status, description))
            client_id = cur.fetchone()[0]

        client_data = {
            'client_id': client_id,
            'client_name': client_name,
            'client_contact': client_contact,
            'client_type': client_type,
            'status': status,
            'description': description
        }

        conn.commit()

        QMessageBox.information(None, 'Success', '✅ client added')
        return client_data
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None, 'DB Error', f'⚠️ Failed to add client:\n{e}')


def remove_client(conn, client_id, client_name):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE client
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE client_id = %s
                        """, (client_id,))
        conn.commit()
        QMessageBox.information(None, 'Deleted', f"❌ Client '{client_name}' removed")
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None, 'DB Error', f'⚠️ Failed to delete client:\n{e}')


def edit_client(conn, client_data: dict):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        client_id = client_data.get('client_id')
        client_name = client_data.get('client_name')
        client_contact = client_data.get('client_contact')
        client_type = client_data.get('client_type')
        status = client_data.get('status')
        description = client_data.get('description')
        with conn.cursor() as cur:
            sql = """
                UPDATE client
                SET client_name = %s,
                    client_contact = %s,
                    client_type = %s,
                    status = %s,
                    description = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE client_id = %s
            """
            cur.execute(sql,
                        (client_name, client_contact, client_type,
                         status, description, client_id))
        conn.commit()
        QMessageBox.information(
            None,
            'Edited',
            f"🔄 Client '{client_name}' edited")
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(
            None,
            'DB Error',
            f'⚠️ Failed to edit client:\n{e}')


def client_name_exists(conn, client_name, exclude_id=None):
    """
    Check if a client name already exists in the database.
    exclude_id lets us ignore the current client when editing.
    """
    if not conn:
        QMessageBox.critical(None,
                             'DB Error',
                             '❌ Could not connect to database')
        return None

    with conn.cursor() as cur:
        if exclude_id:
            cur.execute(
                "SELECT 1 "
                "FROM client "
                "WHERE client_name = %s AND client_id <> %s AND deleted_at IS NULL",
                (client_name, exclude_id)
            )
        else:
            cur.execute(
                "SELECT 1 "
                "FROM client "
                "WHERE client_name = %s AND deleted_at IS NULL",
                (client_name,)
            )
        exists = cur.fetchone() is not None
    return exists
