from PySide6.QtWidgets import QMessageBox

def insert_partner(conn, partner_name, partner_contact, description):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO partner (partner_name, partner_contact, description)
                VALUES (%s, %s, %s)
                RETURNING partner_id;
            """

            cur.execute(sql, (partner_name, partner_contact, description))
            partner_id = cur.fetchone()[0]

        partner_data = {
            'partner_id': partner_id,
            'partner_name': partner_name,
            'partner_contact': partner_contact,
            'description': description
        }

        conn.commit()
        QMessageBox.information(None,"Success", "✅ partner added")
        return partner_data
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None,"DB Error", f"⚠️ Failed to add partner:\n{e}")

def remove_partner(conn, partner_id, partner_name):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE partner
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE partner_id = %s
                        """, (partner_id,))
        conn.commit()
        QMessageBox.information(None,'Deleted', f"❌ partner '{partner_name}' removed")
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete partner:\n{e}')

def edit_partner(conn, partner_data:dict):
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    try:
        partner_id = partner_data.get("partner_id")
        partner_name = partner_data.get("partner_name")
        partner_contact = partner_data.get("partner_contact")
        description = partner_data.get("description")
        with conn.cursor() as cur:
            sql =   """
                UPDATE partner
                SET partner_name = %s,
                    partner_contact = %s,
                    description = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE partner_id = %s
            """
            cur.execute(sql, (partner_name, partner_contact, description, partner_id))
        conn.commit()
        QMessageBox.information(None,'Edited', f"🔄 partner '{partner_name}' edited")
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete partner:\n{e}')

def partner_name_exists(conn, partner_name, exclude_id=None):
    """
    Check if a partner name already exists in the database.
    exclude_id lets us ignore the current partner when editing.
    """
    if not conn:
        QMessageBox.critical(None, 'DB Error', '❌ Could not connect to database')
        return None

    with conn.cursor() as cur:
        if exclude_id:
            cur.execute(
                "SELECT 1 FROM partner WHERE partner_name = %s AND partner_id <> %s AND deleted_at IS NULL",
                (partner_name, exclude_id)
            )
        else:
            cur.execute(
                "SELECT 1 FROM partner WHERE partner_name = %s AND deleted_at IS NULL",
                (partner_name,)
            )
        exists = cur.fetchone() is not None
    return exists
