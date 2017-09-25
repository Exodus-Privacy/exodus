# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .models import Report
from exodus.core.dns import *
from exodus.core.http import *

def index(request):
    try:
        reports = Report.objects.order_by('-creation_date')
    except Report.DoesNotExist:
        raise Http404("reports do not exist")
    return render(request, 'reports_list.html', {'reports': reports})

def get_all_apps(request):
    try:
        apps = Application.objects.order_by('handle').distinct('handle')
    except Application.DoesNotExist:
        raise Http404("No apps found")
    return render(request, 'apps_list.html', {'apps': apps})

def search_by_handle(request, handle):
    try:
        reports = Report.objects.order_by('-creation_date').filter(application__handle = handle)
    except Report.DoesNotExist:
        raise Http404("No reports found")
    return render(request, 'reports_list.html', {'reports': reports})

def detail(request, report_id):
    try:
        report = Report.objects.get(pk=report_id)
    except Report.DoesNotExist:
        raise Http404("report does not exist")
    return render(request, 'report_details.html', {'report': report})

def refreshdns(request):
    if request.method == 'GET':
        refresh_dns.delay()
        return HttpResponse(status=200)