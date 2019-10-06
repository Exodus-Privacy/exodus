# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from unittest.mock import patch, Mock, ANY

from reports.models import Application, Report


class ReportsIconTests(TestCase):

    def test_unknown_handle_404s(self):
        response = self.client.get('/reports/com.example.app/latest/icon', follow=True)

        self.assertEqual(response.status_code, 404)

    @patch('reports.views.Minio.get_object', autospec=True, return_value=Mock(data='icon contents'))
    def test_get_by_handle(self, get_object):
        r = Report.objects.create()
        Application.objects.create(report=r, handle='com.example.app', version='1')

        response = self.client.get('/reports/com.example.app/latest/icon', follow=True)

        self.assertTrue(get_object.called)
        self.assertEqual(response.content, b'icon contents')

    @patch('reports.views.Minio.get_object', autospec=True, return_value=Mock(data='icon contents'))
    def test_get_by_handle_returns_latest(self, get_object):
        r1 = Report.objects.create()
        Application.objects.create(report=r1, handle='com.example.app', version='1', icon_path='icon1')
        r2 = Report.objects.create()
        Application.objects.create(report=r2, handle='com.example.app', version='2', icon_path='icon2')

        response = self.client.get('/reports/com.example.app/latest/icon', follow=True)

        get_object.assert_called_once_with(ANY, ANY, 'icon2')
        self.assertEqual(response.content, b'icon contents')

    def test_unknown_id_404s(self):
        response = self.client.get('/reports/123/icon', follow=True)

        self.assertEqual(response.status_code, 404)

    @patch('reports.views.Minio.get_object', autospec=True, return_value=Mock(data='icon contents'))
    def test_get_by_id(self, get_object):
        r = Report.objects.create()
        Application.objects.create(report=r, handle='com.example.app', version='1')

        response = self.client.get('/reports/{}/icon'.format(r.pk), follow=True)

        self.assertTrue(get_object.called)
        self.assertEqual(response.content, b'icon contents')
