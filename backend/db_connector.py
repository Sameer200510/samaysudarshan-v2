import mysql.connector
import os

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            ssl_disabled=False
        )
        print("✅ DB CONNECTED SUCCESSFULLY")
        return conn
    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return None
