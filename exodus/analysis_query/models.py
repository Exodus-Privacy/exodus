# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import requests
from django.core.exceptions import ValidationError

from reports.models import *


def validate_handle(value):
    reg = re.compile(r'^(\w+\.)+\w+$')
    if reg.match(value) is None:
        raise ValidationError(u'%s is not a valid application handle' % value)

    r = requests.get('%s%s' % ('https://play.google.com/store/apps/details?id=', value))
    if r.status_code == 404:
        raise ValidationError(u'%s application not found on Google Play' % value)


class AnalysisRequest(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add = True)
    bucket = models.CharField(max_length = 200, default = '')
    handle = models.CharField(max_length = 500, validators = [validate_handle])
    description = models.TextField(blank = True)
    processed = models.BooleanField(default = False)
    in_error = models.BooleanField(default = False)
    report_id = models.CharField(max_length = 200, default = '')
