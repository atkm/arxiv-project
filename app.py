import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
q = Queue(connection=conn)

from models import *

@app.route('/', methods=['GET', 'POST'])
def index():
    with open(os.path.join(app.config['STATIC_PATH'], 'math_categories.txt')) as f:
        math_categories = f.read().splitlines()
    return render_template('index.html', math_categories=math_categories)

@app.route('/start', methods=['POST'])
def get_keywords_fake():
    data = json.loads(request.data.decode())
    print(data)
    return '1'

def get_keywords():
    data = json.loads(request.data.decode())
    print(data)
    category = data['category']
    #run validation here
    job = q.enqueue_call(
            func = extract_keywords, args=(category,), result_ttl=1000
            )
    return job.get_id()

@app.route('/results/<job_key>', methods=['GET'])
def get_results_fake(job_key):
    return jsonify(['dynamical systems', 'SRB measure', 'Farruh Shahidi'])

def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
                result.result_no_stop_words.items(),
                key=operator.itemgetter(1),
                reverse=True
                )[:10]
        return jsonify(results)
    else:
        return 'Nope!', 202


if __name__ == '__main__':
    app.run()
