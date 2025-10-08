import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1212',
    'database': 'samay_sudarshan_db'
}

try:
    conn = mysql.connector.connect(**db_config)
    print("✅ Connection successful!")
    conn.close()
except mysql.connector.Error as err:
    print("❌ Error:", err)

