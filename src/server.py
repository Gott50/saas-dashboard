import os

from flask import Flask, request, redirect, flash, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or './uploads'
ALLOWED_EXTENSIONS = set(['xlsx', 'xlsm', 'xltx', 'xltm'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)  # TODO fix: RuntimeError: The session is unavailable because no secret key was set.  Set the secret_key on the application to something unique and secret.
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "uploaded %s" % filename
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
