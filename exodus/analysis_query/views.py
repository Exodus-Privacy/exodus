# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import JsonResponse, HttpResponse
from django.http.response import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
            req.source = 'apk'
            req.bucket = str(random_word(60))
            req.description = _('Your request will be handled soon')
            req.save()

            params = StaticAnalysisParameters(req)
            start_static_analysis.delay(params)
            return HttpResponseRedirect(reverse('analysis:wait', args=[req.id]))

    else:
        form = UploadRequestForm()
    return render(request, 'query_upload.html', {'form': form})


class AnalysisRequestView(FormView):
    template_name = 'query_submit.html'
    form_class = AnalysisRequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upload_allowed'] = settings.ALLOW_APK_UPLOAD
        context['submissions_disabled'] = settings.DISABLE_SUBMISSIONS
        return context

    def form_valid(self, form):
        if settings.DISABLE_SUBMISSIONS and not self.request.user.is_superuser:
            # Returns an empty page with 503 status code
            return HttpResponse(status=503)

        randhex = str(random_word(60))
        req = AnalysisRequest(
            handle=form.cleaned_data['handle'],
            source=form.cleaned_data['source'],
            bucket=randhex,
            description=_('Your request will be handled soon')
        )
        req.save()

        params = StaticAnalysisParameters(req)
        start_static_analysis.delay(params)

        return HttpResponseRedirect(reverse('analysis:wait', args=[req.id]))


def wait(request, r_id):
    try:
        analysis = AnalysisRequest.objects.get(pk=r_id)
    except AnalysisRequest.DoesNotExist:
        raise Http404(_("AnalysisRequest does not exist"))
    return render(request, 'query_wait.html', {'analysis': analysis})


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
