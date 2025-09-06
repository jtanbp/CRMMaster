from PySide6.QtWidgets import QMessageBox

def insert_partner(conn, partner_name, partner_contact, description):
    if conn:
        try:
            cur = conn.cursor()

            sql = """
                  INSERT INTO partner (partner_name, partner_contact, description)
                  VALUES (%s, %s, %s) \
                  """

            cur.execute(sql, (partner_name, partner_contact, description))

            conn.commit()
            cur.close()
            QMessageBox.information(None,"Success", "✅ partner added")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,"DB Error", f"⚠️ Failed to add partner:\n{e}")

def remove_partner(conn, partner_id, partner_name):
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                        UPDATE partner
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE partner_id = %s
                        """, (partner_id,))
            conn.commit()
            cur.close()
            QMessageBox.information(None,'Deleted', f"❌ partner '{partner_name}' removed")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete partner:\n{e}')

def edit_partner(conn, partner_data:dict):
    if conn:
        try:
            partner_id = partner_data.get("partner_id")
            partner_name = partner_data.get("partner_name")
            partner_contact = partner_data.get("partner_contact")
            description = partner_data.get("description")
            cur = conn.cursor()
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
            cur.close()
            QMessageBox.information(None,'Edited', f"🔄 partner '{partner_name}' edited")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete partner:\n{e}')