# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from minio import Minio

from reports.models import Report, Application


def index(request):
    return render(request, 'reports_home.html')


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
        raise Http404(_("Report does not exist"))

    reports_number = reports.count()

    paginator = Paginator(reports, settings.EX_PAGINATOR_COUNT)
    reports = paginator.get_page(request.GET.get('page'))

    return render(
        request, 'reports_list.html',
        {
            'reports': reports,
            'reports_count': reports_number,
            'reports_total_count': Report.objects.count(),
            'apps_total_count': Application.objects.distinct('handle').count(),
            'filter': filter,
            'handle': handle
        }
    )


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
        raise Http404(_("Report does not exist"))

    return render(request, 'report_details.html', {'report': report})


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
        settings.MINIO_STORAGE_ENDPOINT,
        access_key=settings.MINIO_STORAGE_ACCESS_KEY,
        secret_key=settings.MINIO_STORAGE_SECRET_KEY,
        secure=settings.MINIO_STORAGE_USE_HTTPS
    )

    try:
        data = minioClient.get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, app.icon_path)
        return HttpResponse(data.data, content_type='image/png')
    except Exception as err:
        print(err)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'android.jpeg'), 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')
