# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Tracker(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    website = models.URLField()

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class DetectionRule(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    pattern = models.CharField(max_length=500)
    description = models.CharField(max_length=20000)

    def __str__(self):
        return self.pattern