from PySide6.QtWidgets import QMessageBox

def insert_client(conn, client_name, client_contact, client_type, status, description):
    if conn:
        try:
            cur = conn.cursor()

            sql = """
                  INSERT INTO client (client_name, client_contact, client_type, status, description)
                  VALUES (%s, %s, %s, %s, %s) \
                  """

            cur.execute(sql, (client_name, client_contact, client_type, status, description))

            conn.commit()
            cur.close()
            QMessageBox.information(None,"Success", "✅ client added")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,"DB Error", f"⚠️ Failed to add client:\n{e}")

def remove_client(conn, client_id, client_name):
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                        UPDATE client
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE client_id = %s
                        """, (client_id,))
            conn.commit()
            cur.close()
            QMessageBox.information(None,'Deleted', f"❌ client '{client_name}' removed")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete client:\n{e}')

def edit_client(conn, client_data:dict):
    if conn:
        try:
            client_id = client_data.get("client_id")
            client_name = client_data.get("client_name")
            client_contact = client_data.get("client_contact")
            client_type = client_data.get("client_type")
            status = client_data.get("status")
            description = client_data.get("description")
            cur = conn.cursor()
            sql =   """
                UPDATE client
                SET client_name = %s,
                    client_contact = %s,
                    client_type = %s,
                    status = %s,
                    description = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE client_id = %s
            """
            cur.execute(sql, (client_name, client_contact, client_type, status, description, client_id))
            conn.commit()
            cur.close()
            QMessageBox.information(None,'Edited', f"🔄 client '{client_name}' edited")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete client:\n{e}')