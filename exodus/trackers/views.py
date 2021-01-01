# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http.response import Http404
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from reports.models import Application, Report
from trackers.models import Tracker


def index(request):
    filter = request.GET.get('filter', None)
    try:
        if filter == 'apps':
            trackers = Tracker.objects.order_by('-apps_number')
        else:
            trackers = Tracker.objects.order_by('name')
    except Tracker.DoesNotExist:
        raise Http404(_("Tracker does not exist"))
    return render(request, 'trackers_list.html', {'trackers': trackers, 'filter': filter})


def detail(request, tracker_id):
    try:
        tracker = Tracker.objects.get(pk=tracker_id)
        # Add spaces aroung pipes for better rendering of signatures
        tracker.network_signature = tracker.network_signature.replace("|", " | ")
        tracker.code_signature = tracker.code_signature.replace("|", " | ")
    except Tracker.DoesNotExist:
        raise Http404(_("Tracker does not exist"))

    reports = Report.objects.filter(found_trackers=tracker_id).order_by('-creation_date')[:settings.EX_PAGINATOR_COUNT]

    data_to_render = {
        'tracker': tracker,
        'reports': reports,
    }
    return render(request, 'tracker_details.html', data_to_render)


def get_stats(request):
    NB_OF_TRACKERS_TO_DISPLAY = 21

    trackers = Tracker.objects.order_by('-apps_number', 'name')[0:NB_OF_TRACKERS_TO_DISPLAY]
    if trackers.count() == 0:
        raise Http404(_("Tracker does not exist"))

    return render(request, 'stats_details.html', {'trackers': trackers})


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


class TrackersListView(ListView):
    template_name = 'trackers_admin_list.html'
    context_object_name = 'trackers'

    def get_queryset(self):
        return Tracker.objects.order_by('-apps_number')
