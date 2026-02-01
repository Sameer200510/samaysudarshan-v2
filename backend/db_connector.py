import mysql.connector

# Database connection details
DB_CONFIG = {
    'user': 'SamaySudarshan',
    'password': '1212',  # <-- CHANGE THIS!
    'host': 'localhost',
    'database': 'samay_sudarshan_db', # <-- Check your database name
    'raise_on_warnings': True
}

def get_db_connection():
    """Returns a connection object to the SamaySudarshan database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        # In a real app, you would log this error and maybe exit.
        return None
import mysql.connector
import os

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            ssl_disabled=False
        )
        print("✅ DB CONNECTED SUCCESSFULLY")
        return conn
    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return None
