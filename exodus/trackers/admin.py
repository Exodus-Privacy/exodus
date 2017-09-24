# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Tracker, DetectionRule

admin.site.register(Tracker)
admin.site.register(DetectionRule)
