from PySide6.QtWidgets import QMessageBox

def insert_supplier(conn, supplier_name, supplier_contact, supplier_type, status, description):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO supplier (supplier_name, supplier_contact, supplier_type, status, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING supplier_id;
            """

            cur.execute(sql, (supplier_name, supplier_contact, supplier_type, status, description))
            supplier_id = cur.fetchone()[0]

        supplier_data = {
            'supplier_id': supplier_id,
            'supplier_name': supplier_name,
            'supplier_contact': supplier_contact,
            'supplier_type': supplier_type,
            'status': status,
            'description': description
        }

        conn.commit()
        QMessageBox.information(None,"Success", "✅ Supplier added")
        return supplier_data
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None,"DB Error", f"⚠️ Failed to add supplier:\n{e}")

def remove_supplier(conn, supplier_id, supplier_name):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE supplier
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE supplier_id = %s
                        """, (supplier_id,))
        conn.commit()
        QMessageBox.information(None,'Deleted', f"❌ Supplier '{supplier_name}' removed")
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete supplier:\n{e}')

def edit_supplier(conn, supplier_data:dict):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        supplier_id = supplier_data.get("supplier_id")
        supplier_name = supplier_data.get("supplier_name")
        supplier_contact = supplier_data.get("supplier_contact")
        supplier_type = supplier_data.get("supplier_type")
        status = supplier_data.get("status")
        description = supplier_data.get("description")
        with conn.cursor() as cur:
            sql =   """
                UPDATE supplier
                SET supplier_name = %s,
                    supplier_contact = %s,
                    supplier_type = %s,
                    status = %s,
                    description = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE supplier_id = %s
            """
            cur.execute(sql, (supplier_name, supplier_contact, supplier_type, status, description, supplier_id))
            conn.commit()
        QMessageBox.information(None,'Edited', f"🔄 Supplier '{supplier_name}' edited")
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete supplier:\n{e}')

def supplier_name_exists(conn, supplier_name, exclude_id=None):
    """
    Check if a supplier name already exists in the database.
    exclude_id lets us ignore the current supplier when editing.
    """
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    with conn.cursor() as cur:
        if exclude_id:
            cur.execute(
                "SELECT 1 FROM supplier WHERE supplier_name = %s AND supplier_id <> %s AND deleted_at IS NULL",
                (supplier_name, exclude_id)
            )
        else:
            cur.execute(
                "SELECT 1 FROM supplier WHERE supplier_name = %s AND deleted_at IS NULL",
                (supplier_name,)
            )
        exists = cur.fetchone() is not None
    return exists
