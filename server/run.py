import sys, os
import json, time
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask
from flask import request
from flask import render_template
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

@app.route('/app/<name>', methods=['GET'])
def app_report(name='fr.meteo'):
    client = MongoClient('localhost', 27017)
    db = client[exodus]
    reports = db[exodus_reports]
    report = reports.find({'application.handle':name}).sort('report.date',pymongo.DESCENDING).limit(1)[0]
    return render_template('app_report.html', report=report)

@app.route('/appid/<idt>', methods=['GET'])
def app_id(idt='0'):
    client = MongoClient('localhost', 27017)
    db = client[exodus]
    reports = db[exodus_reports]
    report = reports.find({"_id": ObjectId(idt)}).limit(1)[0]
    return render_template('app_report.html', report=report)


@app.route('/allreports/<partial>', methods=['GET'])
def all_reports(partial=0):
    client = MongoClient('localhost', 27017)
    db = client[exodus]
    reports = db[exodus_reports]
    r = []
    apps = reports.distinct("application.handle")
    apps.sort()
    trackers = reports.distinct("report.trackers")
    trackers.sort()
    for a in apps: 
        if partial == "0":
            res = reports.find({"$and": [{'application.handle':a}, {'report.partial':{ "$exists": False}}]}).sort('report.date',pymongo.DESCENDING).limit(1)
            if res.count() > 0:
                r.append(res[0])
            # r.append(reports.find({'application.handle':a}).sort('report.date',pymongo.DESCENDING).limit(1)[0])
        else:
            res = reports.find({"$and": [{'application.handle':a}, {'report.partial':{ "$exists": True}}]}).sort('report.date',pymongo.DESCENDING).limit(1)
            if res.count() > 0:
                r.append(res[0])
    return render_template('all_reports.html', reports=r, trackers=trackers)

@app.route('/allreports', methods=['GET'])
def non_partial():
    return all_reports("0")

if __name__ == "__main__":
    manager.run()