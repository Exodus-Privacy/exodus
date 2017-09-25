# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .celery import app
from celery import group, chain, chord
import tempfile
import shutil
from xml.dom import minidom
import sys, os
import zipfile
import subprocess as sp
import yaml
import datetime

from reports.models import Report, Application, Apk, Permission, NetworkAnalysis
from trackers.models import Tracker

def grep(folder, pattern):
    cmd = '/bin/grep -r "%s" %s/' % (pattern, folder)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    return exitCode == 0

@app.task(bind=True)
def find_trackers(self, analysis):
    trackers = Tracker.objects.order_by('name')
    found = []
    for t in trackers:
        print(t.name)
        for p in t.detectionrule_set.all():
            print(p.pattern)
            if grep(analysis.extracted_dir, p.pattern):
                found.append(t)
                break
    return found

@app.task(bind=True)
def extract_apk(self, analysis):
    zip_ref = zipfile.ZipFile(analysis.apk_path, 'r')
    zip_ref.extractall(analysis.extracted_dir)
    zip_ref.close()

@app.task(bind=True)
def get_version(self, analysis):
    yml = os.path.join(analysis.decoded_dir, 'apktool.yml')
    yml_new = os.path.join(analysis.decoded_dir, 'apktool.yml.new')
    cmd = '/bin/cat %s | /bin/grep -v "\!\!" > %s' % (yml, yml_new)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode != 0:
        return ''    
    with open(yml_new) as f:
        dataMap = yaml.safe_load(f)
        return dataMap['versionInfo']['versionName']

@app.task(bind=True)
def get_handle(self, analysis):
    xmldoc = minidom.parse(os.path.join(analysis.decoded_dir, 'AndroidManifest.xml'))
    man = xmldoc.getElementsByTagName('manifest')[0]
    return man.getAttribute('package')

@app.task(bind=True)
def get_permissions(self, analysis):
    xmldoc = minidom.parse(os.path.join(analysis.decoded_dir, 'AndroidManifest.xml'))
    permissions = xmldoc.getElementsByTagName('uses-permission')
    perms = []
    for perm in permissions:
        perms.append(perm.getAttribute('android:name'))
    return perms

@app.task(bind=True)
def sha256sum(self, analysis):
    cmd = '/usr/bin/sha256sum %s | head -c 64' % analysis.apk_path
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    return process.stdout.read()

@app.task(bind=True)
def decode(self, analysis):
    cmd = '/usr/bin/java -jar %s d %s -o %s/' % (analysis.apktool, analysis.apk_path, analysis.decoded_dir)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    return exitCode == 0

@app.task(bind=True)
def download_apk(self, analysis):
    cmd = 'mkdir -p %s' % analysis.query.storage_path
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]

    cmd = 'gplaycli -y -d %s -f %s/' % (analysis.query.handle, analysis.query.storage_path)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    return exitCode == 0

def start_static_analysis(analysis):
    dl_r = download_apk.delay(analysis)
    if not dl_r.get():
        return -1
    g = group(decode.s(analysis), sha256sum.s(analysis), extract_apk.s(analysis))()
    g_r = g.get()
    
    if g_r[0]:
        shasum = g_r[1]
        infos_group = group(get_version.s(analysis), 
                    get_handle.s(analysis),
                    get_permissions.s(analysis),
                    find_trackers.s(analysis),
                    )()
        infos = infos_group.get()
        version = infos[0]
        handle = infos[1]
        perms = infos[2]
        trackers = infos[3]

        report = Report(apk_file=analysis.query.apk, storage_path=analysis.query.storage_path)
        report.save()
        net_analysis = NetworkAnalysis(report=report)
        net_analysis.save()
        report.save()
        app = Application(report=report)
        app.handle = handle
        app.version = version
        app.save(force_insert=True)

        apk = Apk(application = app)
        apk.name = analysis.apk_path
        apk.sum = shasum
        apk.save(force_insert=True)

        for perm in perms:
            p = Permission(application = app)
            p.name = perm
            p.save(force_insert=True)

        report.found_trackers = trackers
        report.save()
        return report.id
    return -1

class StaticAnalysis:
    
    def __init__(self, analysis_query):
        self.query = analysis_query
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        self.apktool = os.path.join(self.root_dir, "apktool.jar")
        self.tmpdir = tempfile.mkdtemp()
        self.decoded_dir = os.path.join(self.tmpdir, 'decoded')
        self.extracted_dir = os.path.join(self.tmpdir, 'extracted')
        self.apk_path = os.path.join(self.query.storage_path, '%s.apk'%self.query.handle)

    def start(self):
        return start_static_analysis(self)