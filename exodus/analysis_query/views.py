# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import FormView, DetailView, ListView
from .forms import AnalysisRequestForm
from .models import AnalysisRequest
from exodus.core.analysis import StaticAnalysis

class AnalysisRequestView(FormView):
    template_name = 'apk_upload.html'
    form_class = AnalysisRequestForm

    def form_valid(self, form):
        analysis_q = AnalysisRequest(
            apk=self.get_form_kwargs().get('files')['apk'])
        analysis_q.save()
        self.id = analysis_q.id

        static = StaticAnalysis(analysis_q)
        static.start()

        return HttpResponseRedirect('/analysis')


class AnalysisRequestListView(ListView):
    template_name = 'queries_list.html'
    context_object_name = 'queries'

    def get_queryset(self):
        return AnalysisRequest.objects.order_by('-uploaded_at')