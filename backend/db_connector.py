import mysql.connector
import os

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("mysql-2e18f1a-sameerlohani200510-a83f.k.aivencloud.com"),
            user=os.getenv("avnadmin"),
            password=os.getenv("AVNS_GUiXbqyo_YnqCSAlh-x"),
            database=os.getenv("defaultdb"),
            port=int(os.getenv("20204")),
            ssl_disabled=False
        )
        print("✅ DB CONNECTED SUCCESSFULLY")
        return conn
    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return None
