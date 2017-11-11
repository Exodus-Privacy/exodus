# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

def index(request):
    return render(request, 'base.html')

def page_not_found(request):
    return render(request, '404.html')