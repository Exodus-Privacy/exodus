# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import render
from django.views.generic import FormView, ListView

from exodus.core.apk import *
from .forms import AnalysisRequestForm
from .models import AnalysisRequest


def randomword(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


class AnalysisRequestView(FormView):
    template_name = 'apk_upload.html'
    form_class = AnalysisRequestForm

    def form_valid(self, form):
        randhex = str(randomword(60))
        analysis_q = AnalysisRequest(handle = form.cleaned_data['handle'], bucket = randhex)
        analysis_q.description = 'Your request will be handled soon'
        analysis_q.save()

        static = StaticAnalysis(analysis_q)
        start_static_analysis.delay(static)

        return HttpResponseRedirect('/analysis/%s' % analysis_q.id)


def wait(request, r_id):
    try:
        r = AnalysisRequest.objects.get(pk = r_id)
    except AnalysisRequest.DoesNotExist:
        raise Http404("AnalysisRequest does not exist")
    return render(request, 'query_wait.html', {'request': r})


def json(request, r_id):
    try:
        r = AnalysisRequest.objects.get(pk = r_id)
    except AnalysisRequest.DoesNotExist:
        raise Http404("AnalysisRequest does not exist")
    r.bucket = ''
    return JsonResponse(model_to_dict(r), safe = False)


class AnalysisRequestListView(ListView):
    template_name = 'queries_list.html'
    context_object_name = 'queries'

    def get_queryset(self):
        return AnalysisRequest.objects.order_by('-uploaded_at')
