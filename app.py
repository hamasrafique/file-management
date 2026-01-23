from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_secret_key_for_dev') # Required for flash messages

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///local.db') # Fallback to sqlite if no DB URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB Max Limit

# --- AWS Configuration ---
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
S3_REGION = os.getenv('AWS_REGION', 'us-east-1')

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=S3_REGION
)

# --- Database Setup ---
db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(255), nullable=False, unique=True)
    size = db.Column(db.Integer, nullable=True) # Size in bytes
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<File {self.name}>'

# Create tables (Run this once or use migrations in production)
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/')
def index():
    files = File.query.order_by(File.upload_date.desc()).all()
    # If using local DB, we might want to ensure at least the list is correct
    return render_template('index.html', files=files) 

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect('/')
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'warning')
        return redirect('/')

    if file:
        filename = secure_filename(file.filename)
        # Generate a unique key to prevent overwrites (timestamp_filename)
        s3_key = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

        try:
            # 1. Calculate size FIRST (before S3 consumes the stream)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0) # Rewind to start for upload

            # 2. Upload to S3
            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={'ContentType': file.content_type}
            )

            # 3. Save Metadata to DB
            new_file = File(name=filename, s3_key=s3_key, size=file_size)
            db.session.add(new_file)
            db.session.commit()
            
            flash('File uploaded successfully!', 'success')
            
        except Exception as e:
            print(f"Error uploading file: {e}")
            flash(f"Error uploading file: {str(e)}", 'error')
            
    return redirect('/')

@app.route('/download/<int:file_id>')
def download(file_id):
    file_record = File.query.get_or_404(file_id)
    
    try:
        # Generate Presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': file_record.s3_key, 'ResponseContentDisposition': f'attachment; filename="{file_record.name}"'},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        return redirect(presigned_url)
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return redirect('/')

@app.route('/preview/<int:file_id>')
def preview(file_id):
    file_record = File.query.get_or_404(file_id)
    
    try:
        # Generate Presigned URL for INLINE viewing (no attachment)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': file_record.s3_key, 'ResponseContentDisposition': 'inline'},
            ExpiresIn=3600
        )
        return redirect(presigned_url)
    except Exception as e:
        print(f"Error generating preview URL: {e}")
        return redirect('/')

@app.route('/delete/<int:file_id>')
def delete(file_id):
    file_record = File.query.get_or_404(file_id)
    
    try:
        # Delete from S3
        s3_client.delete_object(Bucket=S3_BUCKET, Key=file_record.s3_key)
        
        # Delete from DB
        db.session.delete(file_record)
        db.session.commit()
        flash('File deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting file: {e}")
        flash(f"Error deleting file: {str(e)}", 'error')
        
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
