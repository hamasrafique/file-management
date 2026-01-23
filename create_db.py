import pymysql
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def create_database():
    print("[-] Attempting to create database 'filedb'...")
    
    # Parse the DATABASE_URL
    # Format: mysql+pymysql://user:pass@host:port/dbname
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("[!] DATABASE_URL not found in .env")
        return

    try:
        # Extract components
        url = urlparse(db_url)
        username = url.username
        password = url.password
        hostname = url.hostname
        port = url.port or 3306
        dbname = url.path.lstrip('/')

        # Connect to MySQL Server (Root connection, no specific DB)
        connection = pymysql.connect(
            host=hostname,
            user=username,
            password=password,
            port=port,
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Create the database
            sql = f"CREATE DATABASE IF NOT EXISTS {dbname}"
            cursor.execute(sql)
            print(f"[+] Successfully executed: {sql}")
        
        connection.commit()
        connection.close()
        print("[+] Database creation complete! You can now run the app.")
        
    except Exception as e:
        print(f"[x] Failed to create database: {e}")

if __name__ == "__main__":
    create_database()
