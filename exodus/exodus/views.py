# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


def index(request):
    return render(request, 'base.html', {'main_div_class': 'container'})


def page_not_found(request):
    return render(request, '404.html')
