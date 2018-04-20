# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from androguard.core.api_specific_resources import load_permissions
from django.conf import settings
import json
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from minio import Minio
from minio.error import (ResponseError, NoSuchBucket)

from trackers.models import Tracker

MANIFEST_PERMISSIONS = load_permissions(24)

@python_2_unicode_compatible
class Report(models.Model):
    creation_date = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    found_trackers = models.ManyToManyField(Tracker)
    storage_path = models.CharField(max_length = 200, default = '')
    bucket = models.CharField(max_length = 200, default = '')
    apk_file = models.CharField(max_length = 200, default = '')
    pcap_file = models.CharField(max_length = 200, default = '')
    flow_file = models.CharField(max_length = 200, default = '')
    class_list_file = models.CharField(max_length = 200, default = '')

    def __str__(self):
        return self.application.handle

    def trackers(self):
        return self.found_trackers.order_by('name')


class Application(models.Model):
    report = models.OneToOneField(Report, on_delete = models.CASCADE)
    handle = models.CharField(max_length = 200)
    name = models.CharField(max_length = 200, default = '')
    creator = models.CharField(max_length = 200, default = '')
    downloads = models.CharField(max_length = 200, default = '')
    version = models.CharField(max_length = 50)
    version_code = models.CharField(max_length = 50, default = '')
    icon_path = models.CharField(max_length = 500, default = '')
    app_uid = models.CharField(max_length = 128, default = '')
    icon_phash = models.CharField(max_length = 128, default = '')

    def permissions(self):
        return self.permission_set.all().order_by('name')

    @property
    def json_signature(self):
        sign = {
            'handle': self.handle,
            'uaid': self.app_uid,
            'sha256sum': self.apk.sum,
            'name': self.name,
            'version': self.version,
            'version_code': self.version_code,
            'icon_hash': self.icon_phash,
        }
        return json.dumps(sign, indent = 2)


class Apk(models.Model):
    application = models.OneToOneField(Application, on_delete = models.CASCADE)
    name = models.CharField(max_length = 200)
    sum = models.CharField(max_length = 200)


class Certificate(models.Model):
    apk = models.ForeignKey(Apk, on_delete = models.CASCADE)
    has_expired = models.BooleanField(default = False)
    serial_number = models.CharField(max_length = 128, default = '')
    issuer = models.CharField(max_length = 256, default = '')
    subject = models.CharField(max_length = 256, default = '')
    fingerprint = models.CharField(max_length = 256, default = '')


class Permission(models.Model):
    application = models.ForeignKey(Application, on_delete = models.CASCADE)
    name = models.CharField(max_length = 200)

    @property
    def severity(self):
        #perm = str(self.name).split('.')[-1]
        perm = str(self.name)
        if perm in MANIFEST_PERMISSIONS:
            severity = MANIFEST_PERMISSIONS[perm]["protectionLevel"]
            return severity
        return 'normal'

    @property
    def details(self):
        #perm = str(self.name).split('.')[-1]
        perm = str(self.name)
        if perm in MANIFEST_PERMISSIONS:
            return MANIFEST_PERMISSIONS[perm]['description']
        return ''


class NetworkAnalysis(models.Model):
    report = models.ForeignKey(Report, on_delete = models.CASCADE)


class DNSQuery(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete = models.CASCADE)
    hostname = models.CharField(max_length = 200)
    ip = models.CharField(max_length = 200)
    is_tracker = models.BooleanField(default = False)


class HTTPAnalysis(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete = models.CASCADE)


class HTTPPayload(models.Model):
    http_analysis = models.ForeignKey(HTTPAnalysis, on_delete = models.CASCADE)
    destination_uri = models.CharField(max_length = 2000)
    payload = models.CharField(max_length = 20000)
    layer = models.CharField(max_length = 50)


class HTTPSAnalysis(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete = models.CASCADE)


class HTTPSPayload(models.Model):
    https_analysis = models.ForeignKey(HTTPSAnalysis, on_delete = models.CASCADE)
    destination_uri = models.CharField(max_length = 2000)
    payload = models.CharField(max_length = 20000)
    layer = models.CharField(max_length = 50)


class UDPAnalysis(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete = models.CASCADE)


class UDPPayload(models.Model):
    udp_analysis = models.ForeignKey(UDPAnalysis, on_delete = models.CASCADE)
    destination_uri = models.CharField(max_length = 200)
    payload = models.CharField(max_length = 20000)
    layer = models.CharField(max_length = 50)


@receiver(post_delete, sender = Report, dispatch_uid = 'report_delete_signal')
def remove_report_files(sender, instance, using, **kwargs):
    minio_client = Minio(settings.MINIO_URL,
                         access_key = settings.MINIO_ACCESS_KEY,
                         secret_key = settings.MINIO_SECRET_KEY,
                         secure = settings.MINIO_SECURE)
    try:
        objects = minio_client.list_objects(settings.MINIO_BUCKET, prefix = instance.bucket, recursive = True)
        for obj in objects:
            minio_client.remove_object(settings.MINIO_BUCKET, obj.object_name)
    except ResponseError as err:
        print(err)
    except NoSuchBucket as err:
        print(err)
