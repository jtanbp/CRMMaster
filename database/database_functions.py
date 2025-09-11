# 1. Standard Library
import os

# 2. Third Party Library
from dotenv import load_dotenv
import psycopg2  # noqa: I001

# 3. Internal Library


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
