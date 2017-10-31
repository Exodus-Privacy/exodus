import shutil
import zipfile
import subprocess as sp
import yaml
import datetime
import sys, os
import zipfile
import pyshark
import pprint, string
from .celery import app
from reports.models import *
from trackers.models import *

hosts = []
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'hosts.txt')) as file:
    for line in file:
        hosts.append(line.rstrip('\n'))

@app.task(bind=True)
def refresh_dns(self):
    rules = DetectionRule.objects.all()

    print(hosts)
    dns_queries = DNSQuery.objects.all()
    for q in dns_queries:
        q.is_tracker = False
        for r in rules:
            rule = r.pattern.replace('\\', '')
            if q.hostname in rule or rule in q.hostname:
                print('%s  -  %s'%(q.hostname, rule))
                q.is_tracker = True
                # print(r.tracker_id)
                # t = Tracker.objects.get(pk=r.tracker_id)
                # print(t.name)
                # q.tracker = t
                q.save()
                break

        if not q.is_tracker:
            for h in hosts:
                if q.hostname in h or h in q.hostname:
                    print('%s  -  %s'%(q.hostname, h))
                    q.is_tracker = True
                    q.save()
                    break


@app.task(bind=True)
def analyze_dns(self, report_id):
    report = Report.objects.get(pk=report_id)
    net_analysis = NetworkAnalysis.objects.get(report=report)
    cap = pyshark.FileCapture(report.pcap_file)
    for pkt in cap:
        try:
            if pkt.dns and pkt.dns.qry_name and pkt.dns.a:
                qry = DNSQuery(network_analysis=net_analysis)
                qry.ip = pkt.dns.a
                qry.hostname = pkt.dns.qry_name
                qry.save()
        except AttributeError:
            pass
