import mysql.connector
import os
from urllib.parse import urlparse

def get_db_connection():
    try:
        db_url = os.getenv("mysql://avnadmin:AVNS_GUiXbqyo_YnqCSAlh-x@mysql-2e18f1a-sameerlohani200510-a83f.k.aivencloud.com:20204/defaultdb?ssl-mode=REQUIRED")
        if not db_url:
            raise Exception("DATABASE_URL not set")

        url = urlparse(db_url)

        conn = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path.lstrip("/"),
            port=url.port,
            ssl_disabled=False
        )

        print("✅ DB CONNECTED SUCCESSFULLY")
        return conn

    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return None
