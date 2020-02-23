# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from django.core.management import call_command
from django.core.management.base import CommandError
from unittest.mock import patch
from io import StringIO

from trackers.models import Tracker
from trackers.tasks import calculate_trackers_statistics
from reports.models import Application, Report


class TrackersStatsViewTests(TestCase):
    STATS_PATH = '/en/trackers/stats/'

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
        calculate_trackers_statistics()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker.name)
        self.assertEqual(response.context['trackers'][0].apps_number, 0)
        self.assertEqual(response.context['trackers'][0].apps_percent, 0)

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
        calculate_trackers_statistics()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker.name)
        self.assertEqual(response.context['trackers'][0].apps_number, 1)
        self.assertEqual(response.context['trackers'][0].apps_percent, 100)

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
        calculate_trackers_statistics()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker1.name, 1)
        self.assertContains(response, tracker2.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker2.name)
        # Only recent for an application is considered
        self.assertEqual(response.context['trackers'][0].apps_number, 1)
        self.assertEqual(response.context['trackers'][0].apps_percent, 100)
        self.assertEqual(response.context['trackers'][1].name, tracker1.name)
        self.assertEqual(response.context['trackers'][1].apps_number, 1)
        self.assertEqual(response.context['trackers'][1].apps_percent, 100)

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
        calculate_trackers_statistics()

        c = Client()
        response = c.get(self.STATS_PATH)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tracker1.name, 1)
        self.assertContains(response, tracker2.name, 1)
        self.assertEqual(response.context['trackers'][0].name, tracker2.name)
        # Only recent for an application is considered
        self.assertEqual(response.context['trackers'][0].apps_number, 2)
        self.assertEqual(response.context['trackers'][0].apps_percent, 100)
        self.assertEqual(response.context['trackers'][1].name, tracker1.name)
        self.assertEqual(response.context['trackers'][1].apps_number, 1)
        self.assertEqual(response.context['trackers'][1].apps_percent, 50)

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
        calculate_trackers_statistics()

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
        calculate_trackers_statistics()

        c = Client()
        url = self.TRACKER_DETAIL_PATH.format(tracker2.id)
        response = c.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tracker'].id, tracker2.id)
        self.assertEqual(len(response.context['reports']), 2)
        self.assertEqual(response.context['reports'][0].application.handle, application_handle2)
        self.assertEqual(response.context['reports'][0], report3)
        self.assertEqual(response.context['reports'][1].application.handle, application_handle2)
        self.assertEqual(response.context['reports'][1], report2)

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
        calculate_trackers_statistics()

        c = Client()
        url = self.TRACKER_DETAIL_PATH.format(tracker1.id)
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tracker'].id, tracker1.id)
        self.assertEqual(len(response.context['reports']), 1)
        self.assertEqual(response.context['reports'][0].application.handle, application_handle1)
        self.assertEqual(response.context['reports'][0], report1)


class ImportFromEtipCommandTest(TestCase):

    ETIP_API_BASE_URL = 'https://etip.exodus-privacy.eu.org'
    ETIP_API_BASE_PATH = '/api/trackers'

    TRACKER_NOT_IN_EXODUS = {
        'name': 'tracker_1',
        'code_signature': 'code_1',
        'description': 'description 1',
        'network_signature': 'network_1',
        'website': 'https://website1',
        'is_in_exodus': False
    }
    TRACKER_1 = {
        'name': 'tracker_1',
        'code_signature': 'code_1',
        'description': 'description 1',
        'network_signature': 'network_1',
        'website': 'https://website1',
        'is_in_exodus': True
    }
    TRACKER_1_CHANGED = {
        'name': 'tracker_1',
        'code_signature': 'new_code_1',
        'description': 'description 1',
        'network_signature': 'network_1',
        'website': 'https://website1',
        'is_in_exodus': True
    }
    TRACKER_2 = {
        'name': 'tracker_2',
        'code_signature': 'code_2',
        'description': 'description 2',
        'network_signature': 'network_2',
        'website': 'https://website2',
        'is_in_exodus': True
    }

    def test_api_gets_called_correctly(self):
        fake_token = 'fake_token'
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            call_command(
                'import_from_etip',
                token=fake_token,
                stdout=StringIO()
            )
        mocked_get.assert_called_with(
            self.ETIP_API_BASE_URL + self.ETIP_API_BASE_PATH,
            headers={'Authorization': 'Token {}'.format(fake_token)}
        )

    def test_api_gets_called_with_provided_url(self):
        fake_url = 'https://example.com'
        fake_token = 'fake_token'
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            call_command(
                'import_from_etip',
                etip_hostname=fake_url,
                token=fake_token,
                stdout=StringIO(),
            )
        mocked_get.assert_called_with(
            fake_url + self.ETIP_API_BASE_PATH,
            headers={'Authorization': 'Token {}'.format(fake_token)}
        )

    def test_raises_error_when_api_not_200(self):
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 401
            with self.assertRaises(CommandError) as e:
                call_command('import_from_etip', stdout=StringIO())
        error_msg = str(e.exception)
        self.assertEqual(error_msg, 'Unexpected status from API: 401')

    def test_raises_error_when_empty_response(self):
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.json.return_value = []
            with self.assertRaises(CommandError) as e:
                call_command('import_from_etip', stdout=StringIO())
        error_msg = str(e.exception)
        self.assertEqual(error_msg, 'Empty response')

    def _call_command(self, status_code, mocked_json, options=[]):
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = status_code
            mocked_get.return_value.json.return_value = mocked_json
            out = StringIO()
            call_command('import_from_etip', stdout=out, *options)
        return out

    def _create_tracker(self, tracker_data):
        Tracker.objects.create(
            name=tracker_data['name'],
            code_signature=tracker_data['code_signature'],
            description=tracker_data['description'],
            network_signature=tracker_data['network_signature'],
            website=tracker_data['website'],
        )

    def test_ignores_trackers_not_in_exodus(self):
        mocked_json = [self.TRACKER_NOT_IN_EXODUS, self.TRACKER_2]

        out = self._call_command(200, mocked_json)

        self.assertIn("Retrieved 1 trackers from ETIP", out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_2['name']), out.getvalue())

    def test_compares_1_tracker_with_no_changes(self):
        mocked_json = [self.TRACKER_1]
        self._create_tracker(self.TRACKER_1)

        out = self._call_command(200, mocked_json)

        self.assertIn("Retrieved 1 trackers from ETIP", out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_1['name']), out.getvalue())

    def test_compares_1_tracker_with_changes(self):
        self._create_tracker(self.TRACKER_1)
        mocked_json = [self.TRACKER_1_CHANGED]

        out = self._call_command(200, mocked_json)

        self.assertIn("Retrieved 1 trackers from ETIP", out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_1['name']), out.getvalue())
        self.assertIn("Updating code signature from '{}' to '{}'".format(self.TRACKER_1['code_signature'], self.TRACKER_1_CHANGED['code_signature']), out.getvalue())
        self.assertNotIn("Saved changes", out.getvalue())

        tracker = Tracker.objects.get(name=self.TRACKER_1['name'])
        self.assertEquals(tracker.code_signature, self.TRACKER_1['code_signature'])

    def test_compares_1_tracker_with_changes_and_applies(self):
        self._create_tracker(self.TRACKER_1)
        mocked_json = [self.TRACKER_1_CHANGED]

        out = self._call_command(200, mocked_json, ['-a'])

        self.assertIn("Retrieved 1 trackers from ETIP", out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_1['name']), out.getvalue())
        self.assertIn("Updating code signature from '{}' to '{}'".format(self.TRACKER_1['code_signature'], self.TRACKER_1_CHANGED['code_signature']), out.getvalue())
        self.assertIn("Saved changes", out.getvalue())

        tracker = Tracker.objects.get(name=self.TRACKER_1['name'])
        self.assertEquals(tracker.code_signature, self.TRACKER_1_CHANGED['code_signature'])

    def test_compares_with_1_new_tracker(self):
        self._create_tracker(self.TRACKER_1)
        mocked_json = [
            self.TRACKER_1,
            self.TRACKER_2
        ]
        out = self._call_command(200, mocked_json)

        self.assertIn("Retrieved 2 trackers from ETIP", out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_1['name']), out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_2['name']), out.getvalue())
        self.assertIn("Will create new tracker", out.getvalue())

        with self.assertRaises(Tracker.DoesNotExist):
            Tracker.objects.get(name=self.TRACKER_2['name'])

    def test_compares_with_1_new_tracker_and_creates(self):
        self._create_tracker(self.TRACKER_1)
        mocked_json = [
            self.TRACKER_1,
            self.TRACKER_2
        ]
        out = self._call_command(200, mocked_json, ['-a'])

        self.assertIn("Retrieved 2 trackers from ETIP", out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_1['name']), out.getvalue())
        self.assertIn("* Checking {}".format(self.TRACKER_2['name']), out.getvalue())
        self.assertIn("Tracker created", out.getvalue())

        new_tracker = Tracker.objects.get(name=self.TRACKER_2['name'])
        self.assertEquals(new_tracker.name, self.TRACKER_2['name'])
        self.assertEquals(new_tracker.code_signature, self.TRACKER_2['code_signature'])
        self.assertEquals(new_tracker.description, self.TRACKER_2['description'])
        self.assertEquals(new_tracker.network_signature, self.TRACKER_2['network_signature'])
        self.assertEquals(new_tracker.website, self.TRACKER_2['website'])
