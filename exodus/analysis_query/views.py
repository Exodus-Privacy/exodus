# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import render
from django.views.generic import FormView, ListView

from exodus.core.apk import StaticAnalysisParameters, start_static_analysis

from .forms import AnalysisRequestForm, UploadRequestForm
from .models import AnalysisRequest


def random_word(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def upload_file(request):
    if request.method == 'POST' and settings.ALLOW_APK_UPLOAD:
        form = UploadRequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save()
            req.handle = 'from_upload'
            req.bucket = str(random_word(60))
            req.description = _('Your request will be handled soon')
            req.save()

            static = StaticAnalysisParameters(req)
            start_static_analysis.delay(static)
            return HttpResponseRedirect('/analysis/%s' % req.id)
    else:
        form = UploadRequestForm()
    return render(request, 'query_upload.html', {'form': form})


class AnalysisRequestView(FormView):
    template_name = 'query_submit.html'
    form_class = AnalysisRequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upload_allowed'] = settings.ALLOW_APK_UPLOAD
        return context

    def form_valid(self, form):
        randhex = str(random_word(60))
        analysis_q = AnalysisRequest(handle=form.cleaned_data['handle'], bucket=randhex)
        analysis_q.description = _('Your request will be handled soon')
        analysis_q.save()

        static = StaticAnalysisParameters(analysis_q)
        start_static_analysis.delay(static)

        return HttpResponseRedirect('/analysis/%s' % analysis_q.id)


def wait(request, r_id):
    try:
        r = AnalysisRequest.objects.get(pk=r_id)
    except AnalysisRequest.DoesNotExist:
        raise Http404(_("AnalysisRequest does not exist"))
    return render(request, 'query_wait.html', {'request': r})


def json(request, r_id):
    try:
        r = AnalysisRequest.objects.get(pk=r_id)
    except AnalysisRequest.DoesNotExist:
        raise Http404(_("AnalysisRequest does not exist"))

    obj = {
        'description': _(r.description),
        'bucket': '',
        'processed': r.processed,
        'in_error': r.in_error,
        'report_id': r.report_id,
    }

    return JsonResponse(obj, safe=False)


class AnalysisRequestListView(ListView):
    template_name = 'queries_list.html'
    context_object_name = 'queries'

    def get_queryset(self):
        return AnalysisRequest.objects.order_by('-uploaded_at')[:200]
