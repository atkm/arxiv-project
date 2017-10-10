import os
import json
import re
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
from keyword_extraction_db import extract_keywords

@app.route('/', methods=['GET', 'POST'])
def index():
    with open(os.path.join(app.config['STATIC_PATH'], 'math_categories.txt')) as f:
        math_categories = f.read().splitlines()
    return render_template('index.html', math_categories=math_categories)

@app.route('/start', methods=['POST'])
def get_keywords():
    data = json.loads(request.data.decode())
    category = data['category']
    search = Result.query.filter_by(category=category)
    if db.session.query(search.exists()).scalar():
        id = search.first().id
        return '_'.join(['nocompute', str(id)])
    else:
        job = q.enqueue_call(
                func = get_keywords_func, args=(category,), result_ttl=3000
                )
        return job.get_id()

def get_keywords_func(category):
    keywords = extract_keywords(category)
    result = Result(
            category = category,
            keywords = keywords
            )
    db.session.add(result)
    db.session.commit()
    return result.id

@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
    nocompute = re.search('nocompute_(\d+)', job_key)
    if nocompute:
        id = nocompute.group(1)
        return return_keywords(id)
    else:
        job = Job.fetch(job_key, connection=conn)
        if job.is_finished:
            return return_keywords(job.result)
        else:
            return 'Nope!', 202

def return_keywords(id):
    result = Result.query.filter_by(id=id).first()
    return jsonify(result.keywords)


if __name__ == '__main__':
    app.run()
