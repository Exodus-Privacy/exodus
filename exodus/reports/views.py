# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from minio import Minio

from exodus.core.dns import refresh_dns
from reports.models import Report, Application

# Workaround to avoid issue with DB migrations
if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    from .forms import TrackerForm


def _paginate(request, data, per_page=settings.EX_PAGINATOR_COUNT):
    paginator = Paginator(data, per_page)
    page = request.GET.get('page')

    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)

    return paginated_data


def get_reports(request, handle=None):
    filter = request.GET.get('filter', None)
    try:
        if filter == 'no_trackers':
            reports = Report.objects.filter(found_trackers=None).order_by('-creation_date')
        elif filter == 'most_trackers':
            reports = Report.objects.exclude(found_trackers=None).annotate(nb_trackers=Count('found_trackers')).order_by('-nb_trackers')
        else:
            reports = Report.objects.order_by('-creation_date')
            if handle:
                reports = reports.filter(application__handle=handle)
    except Report.DoesNotExist:
        raise Http404(_("reports do not exist"))
    reports_paged = _paginate(request, reports)

    app_count = Application.objects.distinct('handle').count()
    return render(
        request, 'reports_list.html',
        {
            'reports': reports_paged,
            'reports_count': reports.count(),
            'apps_count': app_count,
            'filter': filter,
            'handle': handle
        }
    )


def _get_color_class(count):
    if count == 0:
        color_class = "success"
    elif count < 5:
        color_class = "warning"
    else:
        color_class = "danger"
    return color_class


def detail(request, report_id=None, handle=None):
    try:
        report = None
        if report_id:
            report = Report.objects.get(pk=report_id)
        elif handle:
            report = Report.objects.filter(application__handle=handle).order_by('-creation_date').first()
        if report is None:
            raise Report.DoesNotExist
    except Report.DoesNotExist:
        raise Http404(_("report does not exist"))
    tracker_class = _get_color_class(report.found_trackers.count())
    perm_class = _get_color_class(report.application.permission_set.count())

    return render(
        request, 'report_details.html',
        {
            'report': report,
            'tracker_class': tracker_class,
            'perm_class': perm_class
        }
    )


def refreshdns(request):
    if request.method == 'GET':
        refresh_dns.delay()
        return HttpResponse(status=200)


def get_app_icon(request, app_id=None, handle=None):
    try:
        app = None
        if app_id:
            app = Application.objects.get(pk=app_id)
        elif handle:
            app = Application.objects.filter(handle=handle).order_by('-report__creation_date').first()
        if app is None:
            raise Application.DoesNotExist
    except Application.DoesNotExist:
        raise Http404(_('App does not exist'))

    minioClient = Minio(
        settings.MINIO_URL,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )

    try:
        data = minioClient.get_object(settings.MINIO_BUCKET, app.icon_path)
        return HttpResponse(data.data, content_type='image/png')
    except Exception as err:
        print(err)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'android.jpeg'), 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')


def by_tracker(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            trackers_id = form.cleaned_data.get('trackers')
            try:
                reports_list = Report.objects.order_by('-creation_date')
                for id in trackers_id:
                    reports_list = reports_list.filter(found_trackers=id)
            except Report.DoesNotExist:
                raise Http404("No reports found")

            return render(request, 'reports_by_tracker.html', {'reports': reports_list})

    else:
        form = TrackerForm()

    return render(request, 'search_trackers.html', {'form': form})
