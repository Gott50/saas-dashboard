import os

from flask import Flask, request, redirect, flash, render_template, jsonify
from werkzeug.utils import secure_filename
from bot import Bot
from bot.settings import Settings
from bot.users import Users

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or './uploads'
Settings.assets_location=UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xlsx', 'xlsm', 'xltx', 'xltm'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def make_dir():
    try:
        app.logger.info("mkdir %s" % os.mkdir(UPLOAD_FOLDER))
    except Exception as e:
        app.logger.info(e)


make_dir()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def list_uploads():
    return os.listdir(UPLOAD_FOLDER)


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
    return render_template('upload.html', uploads=list_uploads())


@app.route('/user', methods=['POST'])
def create_checkout():
    bot = init_Bot()

    for f in request.form:
        if not (f == 'username' or f == 'password') and request.form[f] == 'on':
            try:
                app.logger.warning('Starting: %s' % f)
                bot.act(answer_file=f)
            except Exception as e:
                app.logger.warning(e)

    return redirect('/user/%s' % request.form['username'])

def init_Bot():
    if os.environ.get('SELENIUM'):
        bot = Bot(username=request.form['username'],
                  password=request.form['password'],
                  selenium_local_session=False)
        bot.set_selenium_remote_session(
            selenium_url="http://%s:%d/wd/hub" % (os.environ.get('SELENIUM', 'selenium'), 4444))
    else:
        bot = Bot(username=request.form['username'],
                  password=request.form['password'],
                  selenium_local_session=True)
    return bot


@app.route('/user/<username>', methods=['GET'])
def show_user_profile(username):
    if username in Users.users:
        user = Users.users[username]
        return jsonify(user)
    return "User not found: %s" % username


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
