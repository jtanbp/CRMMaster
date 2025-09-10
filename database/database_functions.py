from dotenv import load_dotenv
import os
import psycopg2

def get_connection():
    try:
        #TODO: Set up login for database protection
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

# def test_db(self):
#     conn = get_connection()
#     if conn:
#         cur = conn.cursor()
#         cur.execute('SELECT version();')
#         version = cur.fetchone()
#         self.ui.statusLabel.setText(f"Connected to: {version[0]}")
#         cur.close()
#         conn.close()
#     else:
#         self.ui.statusLabel.setText('Connection failed!')