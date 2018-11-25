# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import requests
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from reports.models import *


def validate_handle(value):
    package_reg = re.compile(r'^(\w+\.)+\w+$')
    if package_reg.match(value) is None:
        raise ValidationError(_(u'%s is not a valid application handle') % value)

    fake_ua_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}
    r = requests.get('%s%s' % ('https://play.google.com/store/apps/details?id=', value), headers=fake_ua_header)
    if r.status_code == 404:
        raise ValidationError(_(u'%s application not found on Google Play') % value)

    duplicate_queries = AnalysisRequest.objects.filter(processed = False, handle = value).count()
    if duplicate_queries > 0:
        raise ValidationError(_('This application is being analyzed.'))

    pending_queries = AnalysisRequest.objects.filter(processed = False).count()
    if pending_queries > 19:
        raise ValidationError(_('Too much pending requests, please retry later'))


class AnalysisRequest(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add = True)
    bucket = models.CharField(max_length = 200, default = '')
    handle = models.CharField(max_length = 500, validators = [validate_handle])
    description = models.TextField(blank = True)
    processed = models.BooleanField(default = False)
    in_error = models.BooleanField(default = False)
    report_id = models.CharField(max_length = 200, default = '')
