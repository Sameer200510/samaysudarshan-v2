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
