from flask import Flask, render_template, request, redirect, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home Page
@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

# Upload File
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect('/')

# Download File
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# Delete File
@app.route('/delete/<filename>')
def delete(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
