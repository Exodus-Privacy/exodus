# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from django.conf import settings

class AnalysisRequest(models.Model):
    #TODO Check file 
    #TODO Use configuration for storage location
    uploaded_at = models.DateField(auto_now_add=True)
    path = 'apks/' + str(uuid.uuid4())
    storage_path = models.TextField(default=path)
    apk = models.FileField(upload_to=path)
    description = models.TextField(blank=True)
    processed = models.BooleanField(default=False)
