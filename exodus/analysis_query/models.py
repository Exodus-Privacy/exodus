# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import requests

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

MAX_QUERIES = 19
PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id='
FAKE_UA_HEADER = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'
}


def validate_handle(handle):
    """
    Validate the given handle
    Check regex, play store url, duplicate queries & total pending queries
    :param handle: application handle to validate
    :raise ValidatioError: if any of the checks fails
    """
    package_reg = re.compile(r'^(\w+\.)+\w+$')
    if package_reg.match(handle) is None:
        error_msg = _(u'%s is not a valid application handle') % handle
        raise ValidationError(error_msg)

    r = requests.get('%s%s' % (PLAY_STORE_URL, handle), headers=FAKE_UA_HEADER)
    if r.status_code == 404:
        raise ValidationError(
            _(u'%s application not found on Google Play') % handle)

    duplicate_queries = AnalysisRequest.objects.filter(
        processed=False,
        handle=handle
    )
    if duplicate_queries.count() > 0:
        raise ValidationError(_('This application is being analyzed.'))

    pending_queries = AnalysisRequest.objects.filter(processed=False).count()
    if pending_queries > MAX_QUERIES:
        raise ValidationError(
            _('Too much pending requests, please retry later'))


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.apk', ]
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension.'))


class AnalysisRequest(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    bucket = models.CharField(max_length=200, default='')
    handle = models.CharField(max_length=500, default='', blank=True, validators=[validate_handle])
    description = models.TextField(blank=True)
    processed = models.BooleanField(default=False)
    in_error = models.BooleanField(default=False)
    report_id = models.CharField(max_length=200, default='')
    apk = models.FileField(blank=False, validators=[validate_file_extension])


@receiver(pre_delete, sender=AnalysisRequest)
def analysis_request_delete(sender, instance, **kwargs):
    instance.apk.delete(False)

