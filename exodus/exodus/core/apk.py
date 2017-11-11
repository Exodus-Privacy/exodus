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
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists)


@app.task(bind=True)
def find_and_save_app_icon(self, analysis):
    return getIcon(analysis.decoded_dir, analysis.icon_name, analysis.apk_tmp)


@app.task(bind=True)
def find_trackers(self, analysis):
    return findTrackers(analysis.decoded_dir)


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
    return getSha256Sum(analysis.apk_tmp)


@app.task(bind=True)
def decode(self, analysis):
    return decodeAPK(analysis.apk_tmp, analysis.decoded_dir)


@app.task(bind=True)
def download_apk(self, analysis):
    # Fix#12 - We have to remove the cached token :S
    shutil.rmtree(os.path.join(str(Path.home()), '.cache/gplaycli/'), ignore_errors=True)

    # cmd = 'mkdir -p %s' % analysis.query.storage_path
    # process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    # output = process.communicate()[0]

    cmd = 'gplaycli -v -t -y -pd %s -f %s/' % (analysis.query.handle, analysis.tmp_dir)
    print(cmd)
    retry = 5
    exit_code = 1
    while retry != 0:
        process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
        output = process.communicate()[0]
        print(output)
        exit_code = ('Error' in str(output))
        if exit_code == 0:
            break
        retry -= 1

    # Upload APK in storage
    if exit_code == 0:
        minioClient = Minio(settings.MINIO_URL,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_SECURE)
        try:
            minioClient.make_bucket(settings.MINIO_BUCKET, location="")
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            print(err)
        try:
            minioClient.fput_object(settings.MINIO_BUCKET, analysis.apk_name, analysis.apk_tmp)
        except ResponseError as err:
            print(err)
    
    return exit_code == 0


@app.task(bind=True)
def get_app_infos(self, analysis):
    """
    Returns the application information
    :param self:
    :param analysis: the analysis query
    :return: the application information
    """
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
        app_info = infos[5]

        # If a report exists for this couple (handle, version), just return it
        existing_report = Report.objects.filter(application__handle=handle, application__version=version).order_by('-creation_date').first()
        if existing_report is not None:
            analysis.clean(True)
            return existing_report.id

        report = Report(apk_file=analysis.apk_name, storage_path='', bucket=analysis.query.bucket)
        report.save()
        net_analysis = NetworkAnalysis(report=report)
        net_analysis.save()
        report.save()
        app = Application(report=report)
        app.handle = handle
        app.version = version
        if app_info is not None:
            app.name = app_info['title']
            app.creator = app_info['creator']
            app.downloads = app_info['downloads']
        if icon_path != '':
            app.icon_path = analysis.icon_name
        app.save(force_insert=True)

        apk = Apk(application = app)
        apk.name = analysis.apk_name
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
        self.bucket = analysis_query.bucket
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        self.apk_tool = os.path.join(self.root_dir, "apktool.jar")
        self.tmp_dir = tempfile.mkdtemp()
        self.decoded_dir = os.path.join(self.tmp_dir, 'decoded')
        self.extracted_dir = os.path.join(self.tmp_dir, 'extracted')
        # self.apk_path = os.path.join(self.query.storage_path, '%s.apk'%self.query.handle)
        self.apk_tmp = os.path.join(self.tmp_dir, '%s.apk'%self.query.handle)
        self.apk_name = '%s_%s.apk' % (self.bucket, self.query.handle)
        self.icon_name = '%s_%s.png' % (self.bucket, self.query.handle)

    def clean(self, remove_from_storage=False):
        print('Removing %s' % self.tmp_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        if remove_from_storage:
            minio_client = Minio(settings.MINIO_URL,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_SECURE)
            try:
                try:
                    objects = minio_client.list_objects(settings.MINIO_BUCKET, prefix=instance.bucket, recursive=True)
                    for obj in objects:
                        minio_client.remove_object(settings.MINIO_BUCKET, obj.object_name)
                except ResponseError as err:
                    print(err)
            except ResponseError as err:
                print(err)

    def start(self):
        return start_static_analysis(self)