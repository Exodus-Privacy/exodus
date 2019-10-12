# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client

from trackers.models import Tracker
from reports.models import Application, Report


class TrackersStatsViewTests(TestCase):
    STATS_PATH = '/en/trackers/stats/'

    def test_should_raise_404_if_no_report(self):
        tracker = Tracker(name='Teemo')
        tracker.save()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 404)

    def test_should_raise_404_if_no_tracker(self):
        report = Report()
        report.save()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 404)

    def test_should_return_stats_with_1_tracker_not_found(self):
        tracker = Tracker(name='Teemo')
        tracker.save()
        report = Report()
        report.save()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker.name)
        self.assertEqual(response.context['trackers'][0].count, 0)
        self.assertEqual(response.context['trackers'][0].score, 0)

    def test_should_return_stats_with_1_tracker_found(self):
        tracker = Tracker(
            id=1,
            name='Teemo',
        )
        tracker.save()
        report = Report()
        report.save()
        report.found_trackers = [tracker.id]
        report.save()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker.name)
        self.assertEqual(response.context['trackers'][0].count, 1)
        self.assertEqual(response.context['trackers'][0].score, 100)

    def test_should_return_stats_with_single_report_one_application(self):
        tracker1 = Tracker(
            id=1,
            name='Teemo',
        )
        tracker1.save()
        tracker2 = Tracker(
            id=2,
            name='Exodus Super Tracker',
        )
        tracker2.save()
        application_handle = "com.exodus.one"
        report1 = Report()
        report1.save()
        application1 = Application(
            handle=application_handle,
            report=report1
        )
        application1.save()
        report1.found_trackers = [tracker2.id]
        report1.save()
        report2 = Report()
        report2.save()
        application2 = Application(
            handle=application_handle,
            report=report2
        )
        application2.save()
        report2.found_trackers = []
        report2.save()
        report3 = Report()
        report3.save()
        application3 = Application(
            handle=application_handle,
            report=report3
        )
        application3.save()
        report3.found_trackers = [tracker1.id, tracker2.id]
        report3.save()

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
        tracker1 = Tracker(
            id=1,
            name='Teemo',
        )
        tracker1.save()
        tracker2 = Tracker(
            id=2,
            name='Exodus Super Tracker',
        )
        tracker2.save()
        application_handle1 = "com.handle.one"
        application_handle2 = "com.handle.two"
        report1 = Report()
        report1.save()
        application1 = Application(
            handle=application_handle1,
            report=report1
        )
        application1.save()
        report1.found_trackers = [tracker2.id]
        report1.save()
        report2 = Report()
        report2.save()
        application2 = Application(
            handle=application_handle2,
            report=report2
        )
        application2.save()
        report2.found_trackers = []
        report2.save()
        report3 = Report()
        report3.save()
        application3 = Application(
            handle=application_handle2,
            report=report3
        )
        application3.save()
        report3.found_trackers = [tracker1.id, tracker2.id]
        report3.save()

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
            tracker = Tracker(name='Tracker{}.'.format(x))
            tracker.save()

        extra_tracker = Tracker(name='Exodus Super Tracker')
        extra_tracker.save()

        first_trackers = Tracker.objects.exclude(name=extra_tracker.name)

        report = Report()
        report.save()
        report.found_trackers = [t.id for t in first_trackers]
        report.save()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, extra_tracker.name)
        for t in first_trackers:
            self.assertContains(response, t.name, 1)
