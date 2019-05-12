# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Tracker, DetectionRule


@admin.register(Tracker)
class TrackerModelAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    search_fields = ['name']
    list_display = ('name', 'code_signature', 'website')


@admin.register(DetectionRule)
class DetectionRuleModelAdmin(admin.ModelAdmin):
    pass
