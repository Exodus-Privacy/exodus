# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from minio import Minio
from minio.error import (ResponseError, NoSuchBucket)

from django.utils import translation
from trackers.models import Tracker
from exodus.core.permissions_en import AOSP_PERMISSIONS_EN
from exodus.core.permissions_fr import AOSP_PERMISSIONS_FR

AOSP_PERMISSIONS = {
    'en': AOSP_PERMISSIONS_EN,
    'fr': AOSP_PERMISSIONS_FR
}


@python_2_unicode_compatible
class Report(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    found_trackers = models.ManyToManyField(Tracker)
    storage_path = models.CharField(max_length=200, default='')
    bucket = models.CharField(max_length=200, default='')
    apk_file = models.CharField(max_length=200, default='')
    pcap_file = models.CharField(max_length=200, default='')
    flow_file = models.CharField(max_length=200, default='')
    class_list_file = models.CharField(max_length=200, default='')

    def __str__(self):
        try:
            handle = self.application.handle
        except Exception:
            handle = "<malformed report>"
        return handle

    def trackers(self):
        return self.found_trackers.order_by('name')


class Application(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    handle = models.CharField(max_length=200)
    name = models.CharField(max_length=200, default='')
    creator = models.CharField(max_length=200, default='')
    downloads = models.CharField(max_length=200, default='')
    version = models.CharField(max_length=50)
    version_code = models.CharField(max_length=50, default='')
    icon_path = models.CharField(max_length=500, default='')
    app_uid = models.CharField(max_length=128, default='')
    icon_phash = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.handle

    def permissions(self):
        return self.permission_set.all().order_by('name')

    def count_dangerous_permissions(self):
        perms = self.permissions()
        count = 0
        for p in perms:
            if p.severity == "Dangerous":
                count += 1
        return count

    def count_special_permissions(self):
        perms = self.permissions()
        count = 0
        for p in perms:
            if p.severity == "Special":
                count += 1
        return count

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
        return json.dumps(sign, indent=2)


class Apk(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    sum = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Certificate(models.Model):
    apk = models.ForeignKey(Apk, on_delete=models.CASCADE)
    has_expired = models.BooleanField(default=False)
    serial_number = models.CharField(max_length=128, default='')
    issuer = models.CharField(max_length=256, default='')
    subject = models.CharField(max_length=256, default='')
    fingerprint = models.CharField(max_length=256, default='')

    def __str__(self):
        return self.fingerprint


class Permission(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_permission_details(self):
        aosp_data = AOSP_PERMISSIONS[translation.get_language()]
        permissions = aosp_data["permissions"]
        perm = permissions.get(self.name, {})
        return perm

    def get_group_details(self):
        aosp_data = AOSP_PERMISSIONS[translation.get_language()]
        groups = aosp_data["groups"]
        group = groups.get(self.group, {})
        return group

    @property
    def short_name(self):
        return str(self.name).split('.')[-1]

    @property
    def prefix(self):
        return '.'.join(str(self.name).split('.')[:-1])

    @property
    def protection_level(self):
        perm = self.get_permission_details()
        protection_level = perm.get("protection_level", "Unknown")
        return protection_level

    @property
    def severity(self):
        # These permissions are defined as "special permissions" by Google
        SPECIAL_PERMISSIONS = [
            "SYSTEM_ALERT_WINDOW",
            "WRITE_SETTINGS"
        ]
        if self.short_name in SPECIAL_PERMISSIONS:
            return "Special"

        protection_level = self.protection_level
        if "dangerous" in protection_level:
            return "Dangerous"
        elif protection_level == "Unknown":
            return "Unknown"
        else:
            return "Normal"

    @property
    def description(self):
        perm = self.get_permission_details()
        description = perm.get("description", "")
        return description

    @property
    def label(self):
        perm = self.get_permission_details()
        label = perm.get("label", "")
        return label

    @property
    def group(self):
        perm = self.get_permission_details()
        group = perm.get("permission_group", "")
        return group

    @property
    def group_icon(self):
        group = self.get_group_details()
        icon = group.get("icon", "")
        return icon


@receiver(post_delete, sender=Report, dispatch_uid='report_delete_signal')
def remove_report_files(sender, instance, using, **kwargs):
    minio_client = Minio(settings.MINIO_STORAGE_ENDPOINT,
                         access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                         secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                         secure=settings.MINIO_STORAGE_USE_HTTPS)
    try:
        objects = minio_client.list_objects(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                            prefix=instance.bucket,
                                            recursive=True)
        for obj in objects:
            minio_client.remove_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, obj.object_name)
    except ResponseError as err:
        print(err)
    except NoSuchBucket as err:
        print(err)
