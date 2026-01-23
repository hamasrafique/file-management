from app import app, db, File, s3_client, S3_BUCKET
import sys

def check_uploads():
    print(f"--- Checking S3 Bucket '{S3_BUCKET}' ---")
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        if 'Contents' in response:
            print(f"[+] Found {response['KeyCount']} files in S3:")
            for obj in response['Contents']:
                print(f"    - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("[-] S3 Bucket is empty.")
    except Exception as e:
        print(f"[x] Error checking S3: {e}")

    print(f"\n--- Checking Database (RDS) ---")
    try:
        with app.app_context():
            files = File.query.all()
            if files:
                print(f"[+] Found {len(files)} records in DB:")
                for f in files:
                    print(f"    - ID: {f.id} | Name: {f.name} | S3 Key: {f.s3_key}")
            else:
                print("[-] Database table 'file' is empty.")
    except Exception as e:
        print(f"[x] Error checking DB: {e}")

if __name__ == "__main__":
    check_uploads()
