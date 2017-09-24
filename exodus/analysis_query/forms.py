# -*- coding: utf-8 -*-
from django import forms
from .models import AnalysisRequest

class AnalysisRequestForm(forms.ModelForm):
    class Meta:
        model = AnalysisRequest
        fields = ('apk','description')