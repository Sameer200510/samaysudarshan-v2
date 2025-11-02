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

# OS/DBMS Perspective: This connection uses the IP/Host (localhost) and port (default 3306) to establish a network connection
# to the running MySQL process, which is managed by the OS. The `user` and `password` are for authentication (DBMS security).