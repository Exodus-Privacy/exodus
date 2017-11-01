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
import string
from pathlib import Path
from django.conf import settings
import shutil
from reports.models import Report, Application, Apk, Permission, NetworkAnalysis
from trackers.models import Tracker
from .static_analysis import *

@app.task(bind=True)
def find_and_save_app_icon(self, analysis):
    return getIcon(analysis.decoded_dir, analysis.query.storage_path, analysis.apk_path)

@app.task(bind=True)
def find_trackers(self, analysis):
    return findTrackers(analysis.decoded_dir)

@app.task(bind=True)
def extract_apk(self, analysis):
    zip_ref = zipfile.ZipFile(analysis.apk_path, 'r')
    zip_ref.extractall(analysis.extracted_dir)
    zip_ref.close()

@app.task(bind=True)
def get_version(self, analysis):
    return getVersion(analysis.decoded_dir)

@app.task(bind=True)
def get_handle(self, analysis):
    return getHandle(analysis.decoded_dir)

@app.task(bind=True)
def get_permissions(self, analysis):
    return getPermissions(analysis.decoded_dir)

@app.task(bind=True)
def sha256sum(self, analysis):
    return getSha256Sum(analysis.apk_path)

@app.task(bind=True)
def decode(self, analysis):
    return decodeAPK(analysis.apk_path, analysis.decoded_dir)

@app.task(bind=True)
def download_apk(self, analysis):
    # Fix#12 - We have to remove the cached token :S
    shutil.rmtree(os.path.join(str(Path.home()), '.cache/gplaycli/'), ignore_errors=True)

    cmd = 'mkdir -p %s' % analysis.query.storage_path
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]

    cmd = 'gplaycli -t -y -d %s -f %s/' % (analysis.query.handle, analysis.query.storage_path)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = ('Error' in str(output))
    return exitCode == 0

@app.task(bind=True)
def get_app_infos(self, analysis):
    return getApplicationInfos(analysis.query.handle)

def start_static_analysis(analysis):
    dl_r = download_apk.delay(analysis)
    if not dl_r.get():
        return -1
    g = group(decode.s(analysis), sha256sum.s(analysis))()
    g_r = g.get()
    
    if g_r[0]:
        shasum = g_r[1]
        infos_group = group(get_version.s(analysis), 
                    get_handle.s(analysis),
                    get_permissions.s(analysis),
                    find_trackers.s(analysis),
                    find_and_save_app_icon.s(analysis),
                    get_app_infos.s(analysis),
                    )()
        infos = infos_group.get()
        version = infos[0]
        handle = infos[1]
        perms = infos[2]
        trackers = infos[3]
        icon_path = infos[4]
        app_infos = infos[5]

        # If a report exists for this couple (handle, version), just return it
        existing_report = Report.objects.filter(application__handle=handle, application__version=version).order_by('-creation_date').first()
        if existing_report != None:
            analysis.clean(True)
            return existing_report.id

        report = Report(apk_file=analysis.apk_path, storage_path=analysis.query.storage_path)
        report.save()
        net_analysis = NetworkAnalysis(report=report)
        net_analysis.save()
        report.save()
        app = Application(report=report)
        app.handle = handle
        app.version = version
        if app_infos is not None:
            app.name = app_infos['title']
            app.creator = app_infos['creator']
            app.downloads = app_infos['downloads']
        if icon_path != '':
            app.icon_path = os.path.relpath(icon_path, settings.EX_FS_ROOT)# Dirty trick to make the icon readable from templates
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

        analysis.clean()

        return report.id
    analysis.clean(True)
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

    def clean(self, remove_from_storage=False):
        print('Removing %s'%self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if remove_from_storage:
            print('Removing %s'%self.query.storage_path)
            shutil.rmtree(self.query.storage_path, ignore_errors=True)

    def start(self):
        return start_static_analysis(self)