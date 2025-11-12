import os
import zipfile
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

# --- Configuration ---
# 'static/themes' is where themes are extracted.
# This directory MUST exist.
UPLOAD_FOLDER = 'static/themes/'
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_theme():
    """
    Handles the theme file upload and extraction.
    ** THIS IS THE VULNERABLE PART **
    """
    if 'theme_file' not in request.files:
        print("Upload Error: No file part in request.")
        return redirect(url_for('index'))
    
    file = request.files['theme_file']

    if file.filename == '':
        print("Upload Error: No file selected.")
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        # We 'sanitize' the filename for the target directory
        # but this is not the vulnerability.
        theme_name = file.filename.rsplit('.', 1)[0]
        
        # Define the target directory for extraction
        # e.g., 'static/themes/my_cool_theme/'
        target_dir = os.path.join(app.config['UPLOAD_FOLDER'], theme_name)
        
        try:
            # Create the theme-specific directory
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            print(f"Target directory created: {target_dir}")

            # --- 🚨 VULNERABILITY HERE 🚨 ---
            #
            # The code directly uses zipfile.extractall() on user-provided
            # input without validating the 'member' filenames within the zip.
            # An attacker can craft a zip file with paths like 
            # '../../../../app.py' to write files outside 'target_dir'.
            #
            
            with zipfile.ZipFile(file, 'r') as zf:
                print(f"Extracting all files from '{file.filename}' to '{target_dir}'...")
                
                # 'extractall' is dangerous! It trusts all paths inside the zip.
                # zf.extractall(path=target_dir)
                for member in zf.infolist():
                    if member.is_dir():
                        continue
                
                    final_path = os.path.join(target_dir, member.filename)

                    os.makedirs(os.path.dirname(final_path), exist_ok=True)

                    with zf.open(member) as source, open(final_path, 'wb') as target:
                        target.write(source.read())
                    
            print("File extraction completed successfully.")
            
        except Exception as e:
            print(f"An error occurred during extraction: {e}")
            return redirect(url_for('index'))
        
        return redirect(url_for('theme_files', theme_name=theme_name))
    
    else:
        print(f"Upload Error: File type not allowed (File: {file.filename})")
        return redirect(url_for('index'))

@app.route('/themes/<theme_name>')
def theme_files(theme_name):
    """A 'dummy' page to show what *should* be in the theme."""
    # This is just to make the lab feel 'real'
    # It lists files in the directory we *thought* we made.
    theme_dir = os.path.join(app.config['UPLOAD_FOLDER'], theme_name)
    try:
        files = os.listdir(theme_dir)
        return f"<h1>Theme '{theme_name}' files:</h1><ul>" + \
               "".join([f"<li>{f}</li>" for f in files]) + \
               "</ul>"
    except Exception as e:
        return f"Could not list theme files: {e}"

if __name__ == '__main__':
    print("Starting vulnerable ZipSlip server...")
    print("Visit http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
