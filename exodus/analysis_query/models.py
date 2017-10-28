# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
import re, requests
import random, string

def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def validate_handle(value):
    reg = re.compile(r'^(\w+\.)+\w+$')
    if reg.match(value) == None :
        raise ValidationError(u'%s is not a valid application handle' % value)
    
    r=requests.get('%s%s' % ('https://play.google.com/store/apps/details?id=', value))
    if r.status_code == 404:
        raise ValidationError(u'%s application not found on Google Play' % value)

class AnalysisRequest(models.Model):
    #TODO Check file 
    #TODO Use configuration for storage location
    uploaded_at = models.DateTimeField(auto_now_add=True)
    path = os.path.join(settings.EX_APK_FS_ROOT, str(randomword(64)))
    storage_path = models.TextField(default=path)
    apk = models.CharField(max_length=500, default='')
    handle = models.CharField(max_length=500,validators=[validate_handle])
    description = models.TextField(blank=True)
    processed = models.BooleanField(default=False)
