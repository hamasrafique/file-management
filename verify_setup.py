from app import app, db, s3_client, S3_BUCKET
import sys

def check_aws():
    print("[-] Checking AWS S3 Connection...")
    try:
        # Simply trying to list buckets or get location to verify creds
        response = s3_client.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        if S3_BUCKET in buckets:
            print(f"[+] Success! Bucket '{S3_BUCKET}' found.")
        else:
            print(f"[!] Warning: Credentials work, but bucket '{S3_BUCKET}' was not found in listing (might be permissions or wrong name).")
            print(f"    Available buckets: {', '.join(buckets[:3])}...")
    except Exception as e:
        print(f"[x] AWS S3 Connection Failed: {e}")
        return False
    return True

def check_db():
    print("[-] Checking Database Connection...")
    try:
        with app.app_context():
            # Try to query the database
            db.engine.connect()
            print("[+] Success! Connected to Database.")
            # Optional: Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if 'file' in tables:
                print(f"[+] 'file' table exists.")
            else:
                print(f"[!] 'file' table does NOT exist. It will be created on first run.")
    except Exception as e:
        print(f"[x] Database Connection Failed: {e}")
        return False
    return True

if __name__ == "__main__":
    print("--- STARTING VERIFICATION ---")
    s3_status = check_aws()
    db_status = check_db()
    
    if s3_status and db_status:
        print("\n[***] VERIFICATION SUCCESSFUL! You are ready to launch. [***]")
    else:
        print("\n[!!!] VERIFICATION FAILED. Please check your .env file. [!!!]")
