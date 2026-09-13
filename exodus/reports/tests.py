# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from unittest.mock import patch, Mock, ANY

from reports.models import Application, Permission, Report
from trackers.models import Tracker


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

    @patch('reports.views.Minio.get_object', autospec=True, return_value=Mock(data='icon contents'))
    def test_icon_is_cached(self, get_object):
        r = Report.objects.create()
        Application.objects.create(report=r, handle='com.example.app', version='1')

        response = self.client.get('/reports/{}/icon'.format(r.pk), follow=True)

        self.assertIn('max-age', response['Cache-Control'])
        self.assertIn('immutable', response['Cache-Control'])

    @patch('reports.views.Minio.get_object', autospec=True, side_effect=Exception('minio unavailable'))
    def test_falls_back_to_default_icon_without_cache_when_minio_fails(self, get_object):
        r = Report.objects.create()
        Application.objects.create(report=r, handle='com.example.app', version='1')

        response = self.client.get('/reports/{}/icon'.format(r.pk), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        self.assertFalse(response.has_header('Cache-Control'))


class ReportsViewTests(TestCase):
    REPORTS_PATH = '/en/reports/list/'

    def test_should_return_reports_total_count_with_2_reports(self):
        Report.objects.create()
        Report.objects.create()

        response = self.client.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reports_total_count'], 2)

    def test_should_return_apps_total_count_with_2_applications(self):
        r1 = Report.objects.create()
        r2 = Report.objects.create()
        Application.objects.create(name="App1", report=r1, handle="com.test.track1")
        Application.objects.create(name="App2", report=r2, handle="com.test.track2")

        response = self.client.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['apps_total_count'], 2)

    def test_should_return_apps_total_count_with_2_applications_using_same_handle(self):
        r1 = Report.objects.create()
        r2 = Report.objects.create()
        Application.objects.create(name="App1", report=r1, handle="com.test.track")
        Application.objects.create(name="App2", report=r2, handle="com.test.track")

        response = self.client.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['apps_total_count'], 1)

    def test_should_ensure_reports_total_count_stays_with_filter_most_trackers(self):
        Report.objects.create()
        Report.objects.create()

        response = self.client.get(self.REPORTS_PATH + "?filter=most_trackers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reports_total_count'], 2)

    def test_should_ensure_reports_total_count_stays_with_filter_no_trackers(self):
        Report.objects.create()
        Report.objects.create()

        response = self.client.get(self.REPORTS_PATH + "?filter=no_trackers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reports_total_count'], 2)

    def test_should_render_tracker_and_permission_count_badges(self):
        report = Report.objects.create()
        trackers = [Tracker.objects.create(name='Tracker{}'.format(i)) for i in range(6)]
        report.found_trackers.set([t.id for t in trackers])
        app = Application.objects.create(report=report, handle='com.test.app', version='1')
        Permission.objects.create(application=app, name='android.permission.CAMERA')

        response = self.client.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'badge-danger reports">6<')
        self.assertContains(response, 'badge-warning reports">1<')

    def test_should_render_report_without_application(self):
        Report.objects.create()

        response = self.client.get(self.REPORTS_PATH)

        self.assertEqual(response.status_code, 200)

    def test_should_paginate_reports(self):
        for _ in range(settings.EX_PAGINATOR_COUNT + 1):
            Report.objects.create()

        response = self.client.get(self.REPORTS_PATH + '?page=2')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reports'].paginator.num_pages, 2)
        self.assertEqual(len(response.context['reports']), 1)

    def _create_full_report(self, handle):
        report = Report.objects.create()
        report.found_trackers.set([Tracker.objects.create(name='T-' + handle).id])
        app = Application.objects.create(report=report, handle=handle, version='1')
        Permission.objects.create(application=app, name='android.permission.CAMERA')

    def _count_list_view_queries(self):
        with CaptureQueriesContext(connection) as ctx:
            self.client.get(self.REPORTS_PATH)
        return len(ctx.captured_queries)

    def test_list_view_has_no_n_plus_1(self):
        self._create_full_report('com.test.one')
        baseline = self._count_list_view_queries()

        for i in range(5):
            self._create_full_report('com.test.{}'.format(i))

        self.assertEqual(self._count_list_view_queries(), baseline)
