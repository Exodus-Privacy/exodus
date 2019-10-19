# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


def index(request):
    return render(request, 'home.html')


def permissions(request):
    return render(request, 'permissions.html')


def trackers(request):
    return render(request, 'trackers.html')


def next(request):
    return render(request, 'next.html')


def understand(request):
    return render(request, 'understand.html')


def organization(request):
    return render(request, 'organization.html')


def page_not_found(request):
    return render(request, '404.html')
