# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from reports.models import Application, Report


class RestfulApiGetAllApplicationsTests(APITestCase):

    def force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_empty_json_when_no_applications(self):
        self.force_authentication()
        response = self.client.get('/api/applications')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['applications'], [])

    def test_returns_applications_with_report_last_update(self):
        self.force_authentication()
        report = Report()
        report.save()
        application = Application(
            name='app_name',
            handle='handle',
            report=report
        )
        application.save()

        response = self.client.get('/api/applications')

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
