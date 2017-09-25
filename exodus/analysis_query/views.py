# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import FormView, DetailView, ListView
from .forms import AnalysisRequestForm
from .models import AnalysisRequest
from exodus.core.apk import StaticAnalysis
from django.core.exceptions import ValidationError

class AnalysisRequestView(FormView):
    template_name = 'apk_upload.html'
    form_class = AnalysisRequestForm

    def form_valid(self, form):
        analysis_q = AnalysisRequest(handle=form.cleaned_data['handle'])
        analysis_q.save()

        static = StaticAnalysis(analysis_q)
        r_id = static.start()
        if r_id < 0:
            raise ValidationError('Unable to analyze the APK file')

        return HttpResponseRedirect('/reports/%s/'%r_id)

class AnalysisRequestListView(ListView):
    template_name = 'queries_list.html'
    context_object_name = 'queries'

    def get_queryset(self):
        return AnalysisRequest.objects.order_by('-uploaded_at')