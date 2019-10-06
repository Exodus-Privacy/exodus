# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
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


class ReportsViewTests(TestCase):
    REPORTS_PATH = '/en/reports/'

    def test_should_return_reports_count_with_2_reports(self):
        Report.objects.create()
        Report.objects.create()

        c = Client()
        response = c.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reports_count'], 2)

    def test_should_return_apps_count_with_2_applications(self):
        r1 = Report.objects.create()
        r2 = Report.objects.create()
        Application.objects.create(name="App1", report=r1, handle="com.test.track1")
        Application.objects.create(name="App2", report=r2, handle="com.test.track2")

        c = Client()
        response = c.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['apps_count'], 2)

    def test_should_return_apps_count_with_2_applications_using_same_handle(self):
        r1 = Report.objects.create()
        r2 = Report.objects.create()
        Application.objects.create(name="App1", report=r1, handle="com.test.track")
        Application.objects.create(name="App2", report=r2, handle="com.test.track")

        c = Client()
        response = c.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['apps_count'], 1)
