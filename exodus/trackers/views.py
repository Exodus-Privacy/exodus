# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from .models import Tracker, DetectionRule

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