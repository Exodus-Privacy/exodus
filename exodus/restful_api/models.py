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

