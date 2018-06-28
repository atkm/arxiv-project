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
from keyword_extraction_db import extract_keywords, load_data

@app.route('/', methods=['GET', 'POST'])
def index():
    with open(os.path.join(app.config['STATIC_PATH'], 'math_categories.txt')) as f:
        math_categories = f.read().splitlines()
    return render_template('index.html', math_categories=math_categories)

@app.route('/start', methods=['POST'])
def get_keywords():
    data = json.loads(request.data.decode())
    category = data['category']
    specificity = data['specificity']
    search = Result.query.filter_by(category=category)
    if db.session.query(search.exists()).scalar():
        id = search.first().id
        return '_'.join(['nocompute', str(id)])
    else:
        print('Queuing a job for ({}, {}).'.format(category, specificity))
        job = q.enqueue_call(
                func = get_keywords_func, args=(category,specificity), result_ttl=3000 #unit = seconds
                )
        return job.get_id()

# specificity is an integer between 1 and 4, inclusive.
# The higher the value, the more specific keywords get.
# Roughly, specificity -> expected cluster size:
# 1 -> 400, 2 -> 200, 3 -> 100, 4 -> 50.
def get_keywords_func(category, specificity):
    print('Category: {}, specificity: {}'.format(category, specificity))
    abstracts = load_data(category)
    n_abstracts = abstracts.shape[0]
    expected_cluster_size = specificity_to_cluster_size(specificity)
    K = n_abstracts // expected_cluster_size
    topN = 5 # TODO: modify topN according to K
    print('n_abstracts: {}, K: {}, expected_cluster_size: {}'.format(n_abstracts, K, expected_cluster_size))
    keywords = extract_keywords(abstracts, K, topN)
    result = Result(
            category = category,
            keywords = keywords
            )
    db.session.add(result)
    db.session.commit()
    return result.id

def specificity_to_cluster_size(specificity):
    if (specificity == '1'):
        return 400
    elif (specificity == '2'):
        return 200
    elif (specificity == '3'):
        return 100
    elif (specificity == '4'):
        return 50
    else:
        raise ValueError("Invalid specificity")
    

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
