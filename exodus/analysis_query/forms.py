# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import AnalysisRequest


class AnalysisRequestForm(forms.ModelForm):
    class Meta:
        model = AnalysisRequest
        fields = ('handle', 'source')

    def clean(self):
        cleaned_data = super().clean()
        handle = cleaned_data.get('handle')
        if not handle:
            self.add_error('handle', _('A handle is required to submit an analysis.'))
        return cleaned_data


class UploadRequestForm(forms.ModelForm):
    class Meta:
        model = AnalysisRequest
        fields = ('apk', )
