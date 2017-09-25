import shutil
import zipfile
import subprocess as sp
import yaml
import datetime
import sys, os
import zipfile
import pyshark
import pprint
from .celery import app
from reports.models import *
from trackers.models import Tracker

@app.task(bind=True)
def analyze_http(self, report_id):
    report = Report.objects.get(pk=report_id)
    net_analysis = NetworkAnalysis.objects.get(report=report)

    http_analysis = HTTPAnalysis(network_analysis=net_analysis)
    http_analysis.save()

    cap = pyshark.FileCapture(report.pcap_file)
    for pkt in cap:
        try:
            if pkt.http.request_method == "POST":
                payload=HTTPPayload(http_analysis=http_analysis)
                if pkt.highest_layer != 'HTTP':
                    payload.destination_uri = pkt.http.request_full_uri
                    payload.layer = 'HTTP'
                    payload.payload = pkt.http.__str__() + '\n' + pkt[pkt.highest_layer].__str__()
                    payload.save()
                else:
                    payload.destination_uri = pkt.http.request_full_uri 
                    payload.layer = pkt.highest_layer
                    payload.payload = pkt.http.__str__()
                    payload.save()
        except AttributeError:
            pass