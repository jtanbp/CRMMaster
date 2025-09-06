from PySide6.QtWidgets import QMessageBox

def insert_supplier(conn, supplier_name, supplier_contact, supplier_type, status, description):
    if conn:
        try:
            cur = conn.cursor()

            sql = """
                  INSERT INTO supplier (supplier_name, supplier_contact, supplier_type, status, description)
                  VALUES (%s, %s, %s, %s, %s) \
                  """

            cur.execute(sql, (supplier_name, supplier_contact, supplier_type, status, description))

            conn.commit()
            cur.close()
            QMessageBox.information(None,"Success", "✅ Supplier added")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,"DB Error", f"⚠️ Failed to add supplier:\n{e}")

def remove_supplier(conn, supplier_id, supplier_name):
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                        UPDATE supplier
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE supplier_id = %s
                        """, (supplier_id,))
            conn.commit()
            cur.close()
            QMessageBox.information(None,'Deleted', f"❌ Supplier '{supplier_name}' removed")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete supplier:\n{e}')

def edit_supplier(conn, supplier_data:dict):
    if conn:
        try:
            supplier_id = supplier_data.get("supplier_id")
            supplier_name = supplier_data.get("supplier_name")
            supplier_contact = supplier_data.get("supplier_contact")
            supplier_type = supplier_data.get("supplier_type")
            status = supplier_data.get("status")
            description = supplier_data.get("description")
            cur = conn.cursor()
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
            cur.close()
            QMessageBox.information(None,'Edited', f"🔄 Supplier '{supplier_name}' edited")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(None,'DB Error', f'⚠️ Failed to delete supplier:\n{e}')