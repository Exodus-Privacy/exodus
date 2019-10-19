# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Tracker

if not settings.TRACKERS_AUTO_UPDATE:
    @admin.register(Tracker)
    class TrackerModelAdmin(admin.ModelAdmin):
        date_hierarchy = 'creation_date'
        search_fields = ['name']
        list_display = ('name', 'code_signature', 'website', 'creation_date')
        change_list_template = 'admin_change_list.html'
        ordering = ('-creation_date',)
        exclude = ('apps_number', 'apps_percent')

        def changelist_view(self, request, extra_context=None):
            # Aggregate new subscribers per day
            chart_data = (
                Tracker.objects.annotate(date=TruncMonth('creation_date'))
                .values('date')
                .annotate(y=Count('id'))
                .order_by('-date')
            )

            # Serialize and attach the chart data to the template context
            as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
            extra_context = extra_context or {'chart_data': as_json}

            # Call the superclass changelist_view to render the page
            return super().changelist_view(request, extra_context=extra_context)
