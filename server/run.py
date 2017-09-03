import sys, os
import json, time
from pymongo import MongoClient
from flask import Flask
from flask import request
from flask_script import Manager
from bson.json_util import dumps, RELAXED_JSON_OPTIONS

exodus = 'exodus'
exodus_reports = 'reports'

app = Flask(__name__)
manager = Manager(app)

@app.route('/report', methods=['POST'])
def post_report():
    client = MongoClient('localhost', 27017)
    db = client[exodus]
    reports = db[exodus_reports]
    reports.insert_one(json.loads(request.get_json()))
    return 'ok'

@app.route('/reports', methods=['GET'])
def get_reports():
    client = MongoClient('localhost', 27017)
    db = client[exodus]
    reports = db[exodus_reports]
    r = []
    for report in reports.find({}):
        r.append(report)
    response = app.response_class(
        response=dumps(r),
        status=200,
        mimetype='application/json'
    )
    return response

    
if __name__ == "__main__":
    manager.run()