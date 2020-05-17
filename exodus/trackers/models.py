# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Tracker(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    code_signature = models.CharField(max_length=500, blank=True, default='')
    network_signature = models.CharField(max_length=500, blank=True, default='')
    website = models.URLField()
    apps_number = models.IntegerField(default=0)
    apps_percent = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_color_class(self):
        if self.apps_percent >= 50:
            tracker_class = "danger"
        elif self.apps_percent >= 33:
            tracker_class = "alert"
        elif self.apps_percent >= 20:
            tracker_class = "warning"
        else:
            tracker_class = "info"
        return tracker_class


@python_2_unicode_compatible
class DetectionRule(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    pattern = models.CharField(max_length=500)
    description = models.CharField(max_length=20000)

    def __str__(self):
        return self.pattern
