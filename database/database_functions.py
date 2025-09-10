from dotenv import load_dotenv
import os
import psycopg2

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname='onexdb',
            user='jtan',
            password='parkgreen',
            host='localhost',
            port=5432
        )
        #TODO: Set up login for database protection
        # load_dotenv()
        # DATABASE_URL = os.getenv('DATABASE_URL')
        # conn = psycopg2.connect(DATABASE_URL)
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