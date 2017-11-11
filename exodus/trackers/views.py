# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from .models import *
from reports.models import *


def index(request):
    try:
        trackers = Tracker.objects.order_by('name')
    except Tracker.DoesNotExist:
        raise Http404("trackers does not exist")
    return render(request, 'trackers_list.html', {'trackers': trackers})


def detail(request, tracker_id):
    try:
        tracker = Tracker.objects.get(pk=tracker_id)
    except Tracker.DoesNotExist:
        raise Http404("tracker does not exist")
    return render(request, 'tracker_details.html', {'tracker': tracker})


def graph(request):
    try:
        g = "digraph {<br>"
        reports = Report.objects.order_by('-creation_date')
        u_t = Tracker.objects.distinct('name')
        for t in u_t:
            g += "t%s[group=\"tracker\", label=\"%s\"];<br>"%(t.id,t.name)
        u_a = Application.objects.distinct('handle')
        for a in u_a:
            g += "a%s[group=\"app\", label=\"%s\"];<br>"%(a.id, a.handle)

        for r in reports:
            for t in r.found_trackers.all():
                g += "\ta%s -> t%s;<br>"%(r.application.id, t.id)

        g += "<br>}"
    except Tracker.DoesNotExist:
        raise Http404("tracker does not exist")
    return render(request, 'trackers_graph.html', {'g': g})