import os
import json
from flask import Flask, render_template, request, jsonify
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
    return render_template('index.html')

@app.route('/arxiv')
def query():
    pass

if __name__ == '__main__':
    app.run()
