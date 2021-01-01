# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


def index(request):
    return render(request, 'base/home.html')


def permissions(request):
    return render(request, 'base/permissions.html')


def trackers(request):
    return render(request, 'base/trackers.html')


def next(request):
    return render(request, 'base/next.html')


def understand(request):
    return render(request, 'base/understand.html')


def organization(request):
    return render(request, 'base/organization.html')


def page_not_found(request):
    return render(request, 'base/404.html')
