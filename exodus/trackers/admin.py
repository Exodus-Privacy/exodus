# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from .models import Tracker

if not settings.TRACKERS_AUTO_UPDATE:
    @admin.register(Tracker)
    class TrackerModelAdmin(admin.ModelAdmin):
        date_hierarchy = 'creation_date'
        search_fields = ['name']
        list_display = ('name', 'code_signature', 'website')
