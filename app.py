from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
import os
import ocr_service

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me' # Nécessaire pour flash messages

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
RESULTS_FOLDER = os.path.join(os.getcwd(), 'static', 'results')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

# Créer les dossiers s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Vérifier si la requête contient le fichier
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Traitement OCR
            try:
                results = ocr_service.process_file(filepath, app.config['RESULTS_FOLDER'])
                return render_template('index.html', results=results)
            except Exception as e:
                flash(f"Erreur lors du traitement : {str(e)}")
                return redirect(request.url)
        else:
            flash('Type de fichier non autorisé (png, jpg, jpeg, bmp, pdf)')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/results/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

