# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class ReportInfos(models.Model):
    creation_date = models.DateTimeField()
    report_id = models.IntegerField()
    handle = models.CharField(max_length=500)
    apk_dl_link = models.CharField(max_length=500)
    pcap_upload_link = models.CharField(max_length=500)
    flow_upload_link = models.CharField(max_length=500)


class LightReport(models.Model):
    creation_date = models.DateTimeField()
    report_id = models.IntegerField()
    web_report_url = models.CharField(max_length=500)
    api_report_url = models.CharField(max_length=500)
    application_handle = models.CharField(max_length=500)
    application_version = models.CharField(max_length=500)
    application_version_code = models.CharField(max_length=500)
    trackers_count = models.IntegerField()
    permission_count = models.IntegerField()

    def __init__(self, report):
        self.creation_date = report.creation_date
        self.report_id = report.id
        # FixMe get rid of constant string
        self.web_report_url = 'https://reports.exodus-privacy.eu.org/reports/%s/' % report.id
        self.api_report_url = 'https://reports.exodus-privacy.eu.org/api/report/%s/details' % report.id
        self.application_handle = report.application.handle
        self.application_version = report.application.version
        self.application_version_code = report.application.version_code
        self.trackers_count = len(report.found_trackers.all())
        self.permission_count = len(report.application.permissions.all())