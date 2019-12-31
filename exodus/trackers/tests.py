# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client

from trackers.models import Tracker
from reports.models import Application, Report


class TrackersStatsViewTests(TestCase):
    STATS_PATH = '/en/trackers/stats/'

    def test_should_raise_404_if_no_report(self):
        Tracker.objects.create(name='Teemo')

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 404)

    def test_should_raise_404_if_no_tracker(self):
        report = Report.objects.create()
        Application.objects.create(
            handle="apple_sauce",
            report=report
        )

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 404)

    def test_should_return_stats_with_1_tracker_not_found(self):
        tracker = Tracker.objects.create(name='Teemo')
        report = Report.objects.create()
        Application.objects.create(
            handle="apple_sauce",
            report=report
        )

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker.name)
        self.assertEqual(response.context['trackers'][0].count, 0)
        self.assertEqual(response.context['trackers'][0].score, 0)

    def test_should_return_stats_with_1_tracker_found(self):
        tracker = Tracker.objects.create(
            id=1,
            name='Teemo',
        )
        report = Report.objects.create()
        Application.objects.create(
            handle="apple_sauce",
            report=report
        )
        report.found_trackers.set([tracker.id])

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker.name)
        self.assertEqual(response.context['trackers'][0].count, 1)
        self.assertEqual(response.context['trackers'][0].score, 100)

    def test_should_return_stats_with_single_report_one_application(self):
        tracker1 = Tracker.objects.create(
            id=1,
            name='Teemo',
        )
        tracker2 = Tracker.objects.create(
            id=2,
            name='Exodus Super Tracker',
        )
        application_handle = "com.exodus.one"
        report1 = Report.objects.create()
        report1.found_trackers.set([tracker2.id])
        Application.objects.create(
            handle=application_handle,
            report=report1
        )
        report2 = Report.objects.create()
        report2.found_trackers.set([])
        Application.objects.create(
            handle=application_handle,
            report=report2
        )
        report3 = Report.objects.create()
        report3.found_trackers.set([tracker1.id, tracker2.id])
        Application.objects.create(
            handle=application_handle,
            report=report3
        )

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker1.name, 1)
        self.assertContains(response, tracker2.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker2.name)
        # Only recent for an application is considered
        self.assertEqual(response.context['trackers'][0].count, 1)
        self.assertEqual(response.context['trackers'][0].score, 100)
        self.assertEqual(response.context['trackers'][1].name, tracker1.name)
        self.assertEqual(response.context['trackers'][1].count, 1)
        self.assertEqual(response.context['trackers'][1].score, 100)

    def test_should_return_stats_with_multiple_reports_multiple_application(self):
        tracker1 = Tracker.objects.create(
            id=1,
            name='Teemo',
        )
        tracker2 = Tracker.objects.create(
            id=2,
            name='Exodus Super Tracker',
        )
        application_handle1 = "com.handle.one"
        application_handle2 = "com.handle.two"
        report1 = Report.objects.create()
        report1.found_trackers.set([tracker2.id])
        Application.objects.create(
            handle=application_handle1,
            report=report1
        )
        report2 = Report.objects.create()
        report2.found_trackers.set([])
        Application.objects.create(
            handle=application_handle2,
            report=report2
        )
        report3 = Report.objects.create()
        report3.found_trackers.set([tracker1.id, tracker2.id])
        Application.objects.create(
            handle=application_handle2,
            report=report3
        )

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker1.name, 1)
        self.assertContains(response, tracker2.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker2.name)
        # Only recent for an application is considered
        self.assertEqual(response.context['trackers'][0].count, 2)
        self.assertEqual(response.context['trackers'][0].score, 100)
        self.assertEqual(response.context['trackers'][1].name, tracker1.name)
        self.assertEqual(response.context['trackers'][1].count, 1)
        self.assertEqual(response.context['trackers'][1].score, 50)

    def test_should_not_include_more_than_X_trackers(self):
        tracker_limit = 21
        for x in range(0, tracker_limit):
            Tracker.objects.create(name='Tracker{}.'.format(x))

        extra_tracker = Tracker.objects.create(name='Exodus Super Tracker')

        first_trackers = Tracker.objects.exclude(name=extra_tracker.name)

        report = Report.objects.create()
        Application.objects.create(
            handle="apple_sauce",
            report=report
        )
        report.found_trackers.set([t.id for t in first_trackers])

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, extra_tracker.name)
        for t in first_trackers:
            self.assertContains(response, t.name, 1)


class TrackerDetailTestCases(TestCase):
    TRACKER_DETAIL_PATH = "/en/trackers/{}/"

    def test_track_detail_app_multiple_reports(self):
        tracker2 = Tracker.objects.create(
            id=2,
            name='Exodus Super Tracker',
        )
        application_handle2 = "com.handle.two"
        report2 = Report.objects.create()
        report2.found_trackers.set([tracker2.id])
        Application.objects.create(
            handle=application_handle2,
            report=report2
        )
        report3 = Report.objects.create()
        report3.found_trackers.set([tracker2.id])
        Application.objects.create(
            handle=application_handle2,
            report=report3
        )

        c = Client()
        url = self.TRACKER_DETAIL_PATH.format(tracker2.id)
        response = c.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tracker'].id, tracker2.id)
        self.assertEqual(len(response.context['reports']), 1)
        self.assertEqual(response.context['reports'][0].application.handle, application_handle2)
        self.assertEqual(response.context['reports'][0], report3)

    def test_track_detail_app_removed_tracker(self):
        tracker1 = Tracker.objects.create(
            id=1,
            name='Teemo',
        )
        application_handle1 = "com.handle.one"
        report1 = Report.objects.create()
        report1.found_trackers.set([tracker1.id])
        Application.objects.create(
            handle=application_handle1,
            report=report1
        )

        report2 = Report.objects.create()
        # Removing trackers in the version of the app
        report2.found_trackers.set([])
        Application.objects.create(
            handle=application_handle1,
            report=report2
        )

        c = Client()
        url = self.TRACKER_DETAIL_PATH.format(tracker1.id)
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tracker'].id, tracker1.id)
        self.assertEqual(len(response.context['reports']), 0)
