# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import Http404
from django.db import connection
from exodus.core.dns import *
from exodus.core.http import *
from django.conf import settings
import os
from minio import Minio


def index(request):
    try:
        reports = Report.objects.order_by('-creation_date')
        paginator = Paginator(reports, settings.EX_PAGINATOR_COUNT)
        page = request.GET.get('page', 1)
        reports = paginator.page(page)
    except Report.DoesNotExist:
        raise Http404("reports do not exist")
    return render(request, 'reports_list.html', {'reports': reports})


def get_all_apps(request):
    try:
        apps_list = Application.objects.order_by('name', 'handle').distinct('name', 'handle')
    except Application.DoesNotExist:
        raise Http404("No apps found")
    paginator = Paginator(apps_list, settings.EX_PAGINATOR_COUNT)

    page = request.GET.get('page')


    try:
        apps = paginator.page(page)
    except PageNotAnInteger:
        apps = paginator.page(1)
    except EmptyPage:
        apps = paginator.page(paginator.num_pages)
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


def get_app_icon(request, app_id):
    minioClient = Minio(settings.MINIO_URL,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE)
    try:
        app = Application.objects.get(pk=app_id)
    except Application.DoesNotExist:
        raise Http404("app does not exist")

    try:
        data = minioClient.get_object(settings.MINIO_BUCKET, app.icon_path)
        return HttpResponse(data.data, content_type="image/png")
    except Exception as err:
        print(err)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'android.jpeg'), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")


def get_stats(request):
    from collections import namedtuple
    try:
        # reports = NetworkAnalysis.objects.all()
        apps = Application.objects.order_by('name', 'handle').distinct('name', 'handle')
    except Exception as e:
        raise Http404(e)

    cursor = connection.cursor()

    # The part below is unused at the moment (undisplayed stats)
    domain_results = []
    # cursor.execute("select count(hostname) as score, hostname from reports_dnsquery group by hostname having count(hostname) > 3 order by score desc;")
    # desc = cursor.description
    # nt_result = namedtuple('Result', [col[0] for col in desc])
    # domains = [nt_result(*row) for row in cursor.fetchall()]
    # sum = 0
    # for r in reports:
    #     if len(r.dnsquery_set.all()) > 0:
    #         sum += 1
    # for d in domains:
    #     domain_results.append({'hostname':d.hostname, 'score':int(100.*d.score/sum)})

    tracker_query = """
        SELECT tt.name, tt.id, COUNT(*) as c
        FROM reports_report_found_trackers AS ft, trackers_tracker AS tt
        WHERE tt.id = ft.tracker_id
        GROUP BY ft.tracker_id, tt.name, tt.id
        ORDER BY c
        DESC LIMIT 21;
    """
    cursor.execute(tracker_query)
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    trackers = [nt_result(*row) for row in cursor.fetchall()]

    sum = len(apps)
    tracker_results = []
    for t in trackers:
        tracker_results.append({'id': t.id, 'name': t.name, 'score': int(100.*t.c/sum), 'count': int(t.c)})

    return render(request, 'stats_details.html', {'domains': domain_results, 'trackers': tracker_results})
