# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from trackers.models import Tracker

class Report(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    found_trackers = models.ManyToManyField(Tracker)
    storage_path = models.CharField(max_length=200, default='')
    apk_file = models.CharField(max_length=200, default='')
    pcap_file = models.CharField(max_length=200, default='')
    flow_file = models.CharField(max_length=200, default='')

class Application(models.Model):
    report = models.OneToOneField(Report)
    handle = models.CharField(max_length=200)
    version = models.CharField(max_length=50)

class Apk(models.Model):
    application = models.OneToOneField(Application)
    name = models.CharField(max_length=200)
    sum = models.CharField(max_length=200)

class Permission(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

class NetworkAnalysis(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

class DNSQuery(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=200)
    ip = models.CharField(max_length=200)
    is_tracker = models.BooleanField(default=False)

class HTTPAnalysis(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete=models.CASCADE)

class HTTPPayload(models.Model):
    http_analysis = models.ForeignKey(HTTPAnalysis, on_delete=models.CASCADE)
    destination_uri = models.CharField(max_length=200)
    payload = models.CharField(max_length=20000)
    layer = models.CharField(max_length=50)

class HTTPSAnalysis(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete=models.CASCADE)
    
class HTTPSPayload(models.Model):
    https_analysis = models.ForeignKey(HTTPSAnalysis, on_delete=models.CASCADE)
    destination_uri = models.CharField(max_length=2000)
    payload = models.CharField(max_length=20000)
    layer = models.CharField(max_length=50)

class UDPAnalysis(models.Model):
    network_analysis = models.ForeignKey(NetworkAnalysis, on_delete=models.CASCADE)
    
class UDPPayload(models.Model):
    udp_analysis = models.ForeignKey(UDPAnalysis, on_delete=models.CASCADE)
    destination_uri = models.CharField(max_length=200)
    payload = models.CharField(max_length=20000)
    layer = models.CharField(max_length=50)