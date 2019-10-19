# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.serializers.json import DjangoJSONEncoder

from .models import Report, Application

admin.site.register(Application)


@admin.register(Report)
class ReportModelAdmin(admin.ModelAdmin):
    change_list_template = 'admin_change_list.html'
    date_hierarchy = 'creation_date'
    list_display = ('id', 'application', 'creation_date')
    ordering = ('-creation_date',)

    def changelist_view(self, request, extra_context=None):
        # Aggregate new subscribers per day
        chart_data = (
            Report.objects.annotate(date=TruncMonth('creation_date'))
            .values('date')
            .annotate(y=Count('id'))
            .order_by('-date')
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {'chart_data': as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)
