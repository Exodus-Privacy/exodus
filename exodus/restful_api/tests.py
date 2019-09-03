# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from rest_framework.test import APIClient

from reports.models import Application, Report


class RestfulApiGetAllApplicationsTests(TestCase):

    def test_returns_empty_json_when_no_applications(self):
        client = APIClient()
        response = client.get('/api/applications')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['applications'], [])

    def test_returns_applications_with_report_last_update(self):
        report = Report()
        report.save()
        application = Application(
            name='app_name',
            handle='handle',
            report=report
        )
        application.save()

        client = APIClient()
        response = client.get('/api/applications')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, application.name, 1)

        report_updated_at = application.report.updated_at
        response_application = response.json()['applications'][0]

        self.assertEqual(response_application['name'], application.name)
        self.assertEqual(response_application['handle'], application.handle)
        self.assertEqual(
            response_application['report_updated_at'],
            report_updated_at.timestamp()
        )
