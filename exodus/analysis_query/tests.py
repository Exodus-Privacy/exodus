# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest.mock import patch

from django.test import TestCase

from .forms import AnalysisRequestForm


class AnalysisRequestFormTests(TestCase):

    def test_empty_handle_is_rejected(self):
        form = AnalysisRequestForm(data={'handle': '', 'source': 'google'})

        self.assertFalse(form.is_valid())
        self.assertIn('handle', form.errors)

    @patch('analysis_query.models._is_app_in_store', return_value=True)
    def test_valid_handle_is_accepted(self, mock_store):
        form = AnalysisRequestForm(
            data={'handle': 'com.example.app', 'source': 'google'})

        self.assertTrue(form.is_valid())
