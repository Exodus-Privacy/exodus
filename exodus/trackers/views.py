# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from reports.models import Application, Report
from trackers.models import Tracker


def index(request):
    try:
        trackers = Tracker.objects.order_by('name')
    except Tracker.DoesNotExist:
        raise Http404(_("Tracker does not exist"))
    return render(request, 'trackers_list.html', {'trackers': trackers})


def detail(request, tracker_id):
    reports_number = Report.objects.count()
    try:
        tracker = Tracker.objects.get(pk=tracker_id)
        # Add spaces aroung pipes for better rendering of signatures
        tracker.network_signature = tracker.network_signature.replace("|", " | ")
        tracker.code_signature = tracker.code_signature.replace("|", " | ")
        reports_list = Report.objects.order_by('-creation_date').filter(found_trackers=tracker_id)
    except Tracker.DoesNotExist:

        raise Http404(_("Tracker does not exist"))

    paginator = Paginator(reports_list, settings.EX_PAGINATOR_COUNT)
    page = request.GET.get('page')

    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        reports = paginator.page(1)
    except EmptyPage:
        reports = paginator.page(paginator.num_pages)

    count = reports_list.count()
    score = int(100. * count / reports_number)
    if score >= 50:
        tracker_class = "danger"
    elif score >= 33:
        tracker_class = "warning"
    else:
        tracker_class = "info"

    data_to_render = {
        'tracker': tracker,
        'reports': reports,
        'count': count,
        'score': score,
        'tracker_class': tracker_class
    }
    return render(request, 'tracker_details.html', data_to_render)


def get_stats(request):
    NB_OF_TRACKERS_TO_DISPLAY = 21

    trackers = Tracker.objects.order_by('name')
    reports_number = Report.objects.count()

    if trackers.count() == 0 or reports_number == 0:
        raise Http404(_("report does not exist"))

    for t in trackers:
        t.count = Report.objects.filter(found_trackers=t.id).count()
        t.score = int(100. * t.count / reports_number)

    sorted_trackers = sorted(trackers, key=lambda i: i.count, reverse=True)
    sorted_trackers = sorted_trackers[0:NB_OF_TRACKERS_TO_DISPLAY]

    return render(request, 'stats_details.html', {'trackers': sorted_trackers})


def graph(request):
    try:
        g = "digraph {<br>"
        reports = Report.objects.order_by('-creation_date')
        u_t = Tracker.objects.distinct('name')
        for t in u_t:
            g += "t%s[group=\"tracker\", label=\"%s\"];<br>" % (t.id, t.name)
        u_a = Application.objects.distinct('handle')
        for a in u_a:
            g += "a%s[group=\"app\", label=\"%s\"];<br>" % (a.id, a.handle)

        for r in reports:
            for t in r.found_trackers.all():
                g += "\ta%s -> t%s;<br>" % (r.application.id, t.id)

        g += "<br>}"
    except Tracker.DoesNotExist:
        raise Http404(_("Tracker does not exist"))
    return render(request, 'trackers_graph.html', {'g': g})
