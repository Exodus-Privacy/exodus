# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import FormView, DetailView, ListView
from .forms import AnalysisRequestForm
from .models import AnalysisRequest
from exodus.core.apk import StaticAnalysis
from django.conf import settings
from django.core.exceptions import ValidationError
import random, string, os
from django.shortcuts import render

def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class AnalysisRequestView(FormView):
    template_name = 'apk_upload.html'
    form_class = AnalysisRequestForm

    def form_valid(self, form):
        randhex = str(randomword(60))
        path = os.path.join(settings.EX_APK_FS_ROOT, randhex)
        analysis_q = AnalysisRequest(handle=form.cleaned_data['handle'], storage_path=path, bucket=randhex)
        analysis_q.save()

        static = StaticAnalysis(analysis_q)
        r_id = static.start()
        if r_id < 0:
            return render(self.request, 'query_error.html', {'error': 'Unable to analyze the APK file'})

        return HttpResponseRedirect('/reports/%s/'%r_id)

class AnalysisRequestListView(ListView):
    template_name = 'queries_list.html'
    context_object_name = 'queries'

    def get_queryset(self):
        return AnalysisRequest.objects.order_by('-uploaded_at')