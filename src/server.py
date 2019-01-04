import os

import redis
from flask import Flask, redirect, flash
from flask import render_template, jsonify, \
    request, current_app
from rq import Queue, Connection
from werkzeug.utils import secure_filename

from bot.config import BaseConfig
from bot.settings import Settings
from bot.tasks import create_task
from bot.users import Users

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or './uploads'
Settings.assets_location = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xlsx', 'xlsm', 'xltx', 'xltm'}

app = Flask(__name__)
app.config.from_object(BaseConfig)
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
    uploads = os.listdir(UPLOAD_FOLDER)[:]
    uploads.sort()
    return uploads


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(
                request.url)  # TODO fix: RuntimeError: The session is unavailable because no secret key was set.  Set the secret_key on the application to something unique and secret.
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


@app.route('/delete', methods=['GET', 'POST'])
def delete_file():
    if request.method == 'POST':
        for f in request.form:
            if request.form[f] == 'on':
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
    return render_template('delete.html', uploads=list_uploads())


@app.route('/user', methods=['POST'])
def create_checkout():
    job_ids = []
    for f in request.form:
        if not (f == 'username' or f == 'password') and request.form[f] == 'on':
            try:
                with Connection(redis.from_url(current_app.config['REDIS_URL'])):
                    q = Queue()
                    job = q.enqueue_call(func=create_task, args=(
                        request.form['username'], request.form['password'], f, (pars_sleep())),
                                         job_id="%s: %s" % (request.form['username'], f))
                    job_ids += [job.get_id()]
            except redis.exceptions.ConnectionError:
                create_task(request.form['username'], request.form['password'], f, (pars_sleep()))
    response_object = {
        'status': 'success',
        'data': {
            'job_ids': job_ids
        }
    }
    return jsonify(response_object), 202


def pars_sleep():
    try:
        return int(request.form["sleep"])
    except ValueError:
        return None


@app.route('/jobs/<job_id>', methods=['GET'])
def get_status(job_id):
    with Connection(redis.from_url(current_app.config['REDIS_URL'])):
        q = Queue()
        job = q.fetch_job(job_id)
    if job:
        response_object = {
            'status': 'success',
            'data': get_job_data(job)
        }
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)


@app.route('/jobs/status', methods=['POST'])
def get_jobs_status():
    try:
        jobs = []
        for job_id in request.get_json():
            with Connection(redis.from_url(current_app.config['REDIS_URL'])):
                q = Queue()
                job = q.fetch_job(job_id)
            if job:
                jobs += [get_job_data(job)]
            else:
                return jsonify({'status': 'error'})
        result = {
            'status': 'success',
            'data': {
                'jobs': jobs
            }
        }
        return jsonify(result)
    except Exception as e:
        app.logger.error("Exception at get_jobs_status(): %s" % e)
        app.logger.error("result: %s" % result)


@app.route('/jobs', methods=['GET'])
def get_jobs():
    try:
        with Connection(redis.from_url(current_app.config['REDIS_URL'])):
            q = Queue()
            jobs = q.jobs
        if jobs:
            response_object = {
                'status': 'success',
                'data': {
                    'jobs': list(map(lambda job: get_job_data(job), jobs))
                }
            }
        else:
            response_object = {'status': 'error', 'message': 'no job found'}
    except Exception as e:
        response_object = {'status': 'error', 'message': str(e)}
    return jsonify(response_object)


def get_job_data(job):
    return {
        'job_id': job.get_id(),
        'job_status': job.get_status(),
        'job_result': job.result,
        'job_meta': job.meta,
    }


@app.route('/user', methods=['GET'])
def list_user():
    return render_template("user_list.html", users=Users.users)


@app.route('/user', methods=['POST'])
def upload_user():
    return "Not Implemented", 501


@app.route('/user/<username>', methods=['GET'])
def show_user_profile(username):
    if username in Users.users:
        user = Users.users[username]
        return compose_user_view(user)
    return render_template('user_not_found.html', username=username)


def compose_user_view(user):
    view = render_template('user_prefix.html')

    for test in user:
        view += '<h1 id="%s">%s</h1>' % (test, test)
        view += user[test].replace('style="display: none;"', '').replace('style="height: 460px;"', '')

    return view


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
