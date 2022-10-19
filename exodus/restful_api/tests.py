# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from reports.models import Application, Report, Permission, Apk, Certificate
from trackers.models import Tracker, TrackerCategory

DUMMY_HANDLE = 'com.example'


def _get_custom_date_format(date):
    # Not happy with this but creation_date doesn't return the correct format
    return "{}Z".format(date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])


class RestfulApiApplicationTests(APITestCase):
    PATH = '/api/applications'

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_empty_json_when_no_applications(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['applications'], [])

    def test_returns_applications_with_report_last_update(self):
        self._force_authentication()
        report = Report.objects.create(id=1234)
        application = Application.objects.create(
            name='app_name',
            handle='handle',
            source='google',
            report=report
        )

        expected_json = {
            'applications': [
                {
                    "id": application.id,
                    "handle": application.handle,
                    "name": application.name,
                    "creator": "",
                    "downloads": "",
                    "app_uid": "",
                    "source": application.source,
                    "icon_phash": "",
                    "report_updated_at": report.updated_at.timestamp()
                },
            ]
        }

        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

    def test_returns_applications_with_option_short(self):
        self._force_authentication()
        report = Report.objects.create(id=1234)
        application = Application.objects.create(
            name='app_name',
            handle='handle',
            source='google',
            report=report
        )

        expected_json = {
            'applications': [
                {
                    "id": application.id,
                    "handle": application.handle,
                    "app_uid": "",
                    "source": application.source
                },
            ]
        }

        response = self.client.get(self.PATH + '?option=short')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

    def test_returns_applications_with_multiple_versions(self):
        self._force_authentication()
        google_app_report = Report.objects.create(id=1234)
        google_app = Application.objects.create(
            name='app_name',
            handle='handle',
            source='google',
            report=google_app_report
        )
        same_google_app_report = Report.objects.create(id=1235)
        Application.objects.create(
            name='app_name',
            handle='handle',
            source='google',
            report=same_google_app_report
        )
        fdroid_app_report = Report.objects.create(id=1236)
        fdroid_app = Application.objects.create(
            name='app_name',
            handle='handle',
            source='fdroid',
            report=fdroid_app_report
        )

        expected_json = {
            'applications': [
                {
                    "id": google_app.id,
                    "handle": google_app.handle,
                    "app_uid": "",
                    "source": google_app.source
                },
                {
                    "id": fdroid_app.id,
                    "handle": fdroid_app.handle,
                    "app_uid": "",
                    "source": fdroid_app.source
                }
            ]
        }

        response = self.client.get(self.PATH + '?option=short')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiSearchHandleDetailsTests(APITestCase):
    PATH = '/api/search/{}/details'.format(DUMMY_HANDLE)

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_empty_json_when_no_app(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_returns_detailed_json_when_one_app(self):
        tracker = Tracker.objects.create(name='Teemo')
        report = Report.objects.create()
        report.found_trackers.set([tracker.id])
        app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report,
            version="0.1",
            version_code="01234",
            source="google"
        )
        apk = Apk.objects.create(
            application=app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=app,
            name="ALLYOURBASE"
        )

        expected_json = [
            {
                'apk_hash': apk.sum,
                'app_name': app.name,
                'handle': app.handle,
                'report': report.id,
                'trackers': [tracker.id],
                'permissions': ["ALLYOURBASE", "AREBELONGTOUS"],
                'uaid': '',
                'created': _get_custom_date_format(report.creation_date),
                'updated': _get_custom_date_format(report.updated_at),
                'version_code': app.version_code,
                'version_name': app.version,
                'source': app.source,
                'icon_hash': '',
                'downloads': '',
                'creator': ''
            }
        ]

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiSearchHandleTests(APITestCase):
    PATH = '/api/search/{}'.format(DUMMY_HANDLE)

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_empty_json_when_no_app(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})

    def test_returns_detailed_json_when_one_app(self):
        tracker = Tracker.objects.create(name='Teemo')
        report = Report.objects.create()
        report.found_trackers.set([tracker.id])
        app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report,
            version="0.1",
            version_code="01234",
            source="google"
        )
        Apk.objects.create(
            application=app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=app,
            name="ALLYOURBASE"
        )

        expected_json = {
            str(app.handle): {
                'name': app.name,
                'creator': "",
                'reports': [
                    {
                        "id": report.id,
                        "updated_at": _get_custom_date_format(report.updated_at),
                        "creation_date": _get_custom_date_format(report.creation_date),
                        "version": app.version,
                        "version_code": app.version_code,
                        "source": app.source,
                        "downloads": "",
                        "trackers": [tracker.id],
                    }
                ]
            }
        }

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

    def test_returns_detailed_json_when_two_apps(self):
        tracker = Tracker.objects.create(name='Teemo')
        first_report = Report.objects.create()
        first_report.found_trackers.set([tracker.id])
        first_app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=first_report,
            version="0.1",
            version_code="01234",
            source="google"
        )
        Apk.objects.create(
            application=first_app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=first_app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=first_app,
            name="ALLYOURBASE"
        )
        new_report = Report.objects.create()
        new_report.found_trackers.set([tracker.id])
        new_app = Application.objects.create(
            name='new_app_name',
            handle=DUMMY_HANDLE,
            report=new_report,
            version="0.2",
            version_code="01234",
            source="google"
        )
        Apk.objects.create(
            application=new_app,
            name="new_app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=new_app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=new_app,
            name="ALLYOURBASE"
        )

        self.maxDiff = None
        expected_json = {
            str(new_app.handle): {
                'name': new_app.name,
                'creator': "",
                'reports': [
                    {
                        "id": new_report.id,
                        "updated_at": _get_custom_date_format(new_report.updated_at),
                        "creation_date": _get_custom_date_format(new_report.creation_date),
                        "version": new_app.version,
                        "version_code": new_app.version_code,
                        "source": new_app.source,
                        "downloads": "",
                        "trackers": [tracker.id],
                    },
                    {
                        "id": first_report.id,
                        "updated_at": _get_custom_date_format(first_report.updated_at),
                        "creation_date": _get_custom_date_format(first_report.creation_date),
                        "version": first_app.version,
                        "version_code": first_app.version_code,
                        "source": first_app.source,
                        "downloads": "",
                        "trackers": [tracker.id],
                    }
                ]
            }
        }

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiSearchTests(APITestCase):
    PATH = '/api/search'

    # TODO: This endpoint cannot be tested because of the similarity search extension not available on test database
    # def test_returns_empty_json_when_no_app(self):
    #     response = self.client.post(self.PATH, {'limit': 20, 'query': DUMMY_HANDLE, 'type': 'application'}, 'json')

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), {})

    def test_returns_latest_app_when_exact_handle_match(self):
        tracker = Tracker.objects.create(name='Teemo')
        report_first_app = Report.objects.create()
        report_first_app.found_trackers.set([tracker.id])
        first_app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report_first_app,
            version="0.1",
            version_code="01234",
            source="google"
        )
        Apk.objects.create(
            application=first_app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=first_app,
            name="ALLYOURBASE"
        )
        Permission.objects.create(
            application=first_app,
            name="AREBELONGTOUS"
        )
        report_second_app = Report.objects.create()
        report_second_app.found_trackers.set([tracker.id])
        app_with_same_handle = Application.objects.create(
            name='new_app_name',
            handle=DUMMY_HANDLE,
            report=report_second_app,
            version="0.2",
            version_code="01235",
            source="google"
        )
        Apk.objects.create(
            application=app_with_same_handle,
            name="new_app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=app_with_same_handle,
            name="ALLYOURBASE"
        )
        Permission.objects.create(
            application=app_with_same_handle,
            name="AREBELONGTOUS"
        )

        response = self.client.post(self.PATH, {'limit': 20, 'query': DUMMY_HANDLE, 'type': 'application'}, 'json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['handle'], DUMMY_HANDLE)
        self.assertEqual(response.json()['results'][0]['name'], 'new_app_name')


class RestfulApiSearchLatestReportTests(APITestCase):
    PATH = '/api/search/{}/latest'.format(DUMMY_HANDLE)

    def test_returns_empty_json_when_no_app(self):
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})

    def test_returns_data_when_one_app(self):
        report = Report.objects.create()
        Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report,
            version="0.1",
            version_code="01234",
        )

        expected_json = {
            'id': report.id,
            'name': report.application.name,
            'creation_date': _get_custom_date_format(report.creation_date)
        }
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiTrackersTests(APITestCase):
    PATH = '/api/trackers'

    def test_returns_empty_json_when_no_trackers(self):
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['trackers'], {})

    def test_returns_one_tracker(self):
        tracker = Tracker.objects.create(
            name='Teemo',
            description='bad tracker',
            code_signature='com.teemo',
            network_signature='teemo.com',
            website='https://www.example.com'
        )

        expected_json = {
            str(tracker.id): {
                'id': tracker.id,
                'name': tracker.name,
                'description': tracker.description,
                'creation_date': tracker.creation_date.strftime("%Y-%m-%d"),
                'code_signature': tracker.code_signature,
                'network_signature': tracker.network_signature,
                'website': tracker.website,
                'categories': [],
                'documentation': []
            }
        }

        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['trackers'], expected_json)

    def test_returns_one_tracker_with_categories(self):
        tracker = Tracker.objects.create(
            name='Teemo',
            description='bad tracker',
            code_signature='com.teemo',
            network_signature='teemo.com',
            website='https://www.example.com'
        )
        category1 = TrackerCategory.objects.create(name='Analytics')
        category2 = TrackerCategory.objects.create(name='Ads')

        tracker.category.set([category1, category2])

        expected_json = {
            str(tracker.id): {
                'id': tracker.id,
                'name': tracker.name,
                'description': tracker.description,
                'creation_date': tracker.creation_date.strftime("%Y-%m-%d"),
                'code_signature': tracker.code_signature,
                'network_signature': tracker.network_signature,
                'website': tracker.website,
                'categories': ['Analytics', 'Ads'],
                'documentation': []
            }
        }

        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['trackers'], expected_json)

    def test_returns_one_tracker_with_documentation(self):
        tracker = Tracker.objects.create(
            name='Teemo',
            description='bad tracker',
            code_signature='com.teemo',
            network_signature='teemo.com',
            website='https://www.example.com',
            documentation='http://example.com/docs http://example.com/android'
        )

        expected_json = {
            str(tracker.id): {
                'id': tracker.id,
                'name': tracker.name,
                'description': tracker.description,
                'creation_date': tracker.creation_date.strftime("%Y-%m-%d"),
                'code_signature': tracker.code_signature,
                'network_signature': tracker.network_signature,
                'website': tracker.website,
                'categories': [],
                'documentation': ['http://example.com/docs', 'http://example.com/android']
            }
        }

        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['trackers'], expected_json)


class RestfulApiReportTests(APITestCase):
    PATH = '/api/report/1234/'

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_one_report_infos(self):
        self._force_authentication()
        report = Report.objects.create(id=1234)
        app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report
        )

        response = self.client.get(self.PATH)
        expected_json = {
            "creation_date": report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "report_id": report.id,
            "handle": app.handle,
            "apk_dl_link": "",
            "certificate": None
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

    def test_returns_one_report_infos_with_certificate(self):
        self._force_authentication()
        report = Report.objects.create(id=1235)
        app = Application.objects.create(
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report
        )
        apk = Apk.objects.create(
            application=app,
            name="app_name",
            sum="app_checksum"
        )
        Certificate.objects.create(
            apk=apk,
            has_expired=True,
            serial_number="1939892502",
            issuer="Common Name: blokada.org",
            subject="Common Name: blokada.org",
            fingerprint="552AFFE3F863569F9ED05125D52991C2744D2BB3"
        )

        response = self.client.get('/api/report/1235/')
        expected_json = {
            "creation_date": report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "report_id": report.id,
            "handle": app.handle,
            "apk_dl_link": "",
            "certificate": {
                "fingerprint": "552AFFE3F863569F9ED05125D52991C2744D2BB3",
                "has_expired": True,
                "issuer": "Common Name: blokada.org",
                "serial_number": "1939892502",
                "subject": "Common Name: blokada.org"
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

    def test_returns_not_found_when_no_report(self):
        self._force_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 404)


class RestfulApiApkTests(APITestCase):
    PATH = '/api/apk/1/'

    def _force_authentication(self):
        user = User.objects.create_user('user', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def _force_admin_authentication(self):
        user = User.objects.create_superuser('user', 'user@mail', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_forbidden_when_no_admin_auth(self):
        self._force_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 403)

    def test_returns_not_found_when_no_apk(self):
        self._force_admin_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 404)


class RestfulApiReportDetails(APITestCase):
    PATH = '/api/report/1234/details'

    def _force_authentication(self):
        user = User.objects.create_user('user', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_not_found_when_no_report(self):
        self._force_authentication()

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 404)

    def test_returns_detailed_json_when_one_report(self):
        self._force_authentication()

        category = TrackerCategory.objects.create(name='Analytics')
        tracker = Tracker.objects.create(
            name='Teemo',
            description='bad tracker',
            code_signature='com.teemo',
            network_signature='teemo.com',
            website='https://www.example.com',
            documentation='http://example.com/doc'
        )
        tracker.category.set([category])
        report = Report.objects.create(id=1234)
        report.found_trackers.set([tracker.id])
        app = Application.objects.create(
            id=1234,
            name='app_name',
            handle=DUMMY_HANDLE,
            report=report,
            version="0.1",
            version_code="01234",
            source='google'
        )
        Apk.objects.create(
            application=app,
            name="app_name",
            sum="app_checksum"
        )
        Permission.objects.create(
            application=app,
            name="AREBELONGTOUS"
        )
        Permission.objects.create(
            application=app,
            name="ALLYOURBASE"
        )

        expected_json = {
            'creation_date': report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'found_trackers': [
                {
                    'id': tracker.id,
                    'name': tracker.name,
                    'description': tracker.description,
                    'creation_date': tracker.creation_date.strftime("%Y-%m-%d"),
                    'code_signature': tracker.code_signature,
                    'network_signature': tracker.network_signature,
                    'category': [{'name': category.name}],
                    'website': tracker.website,
                    'apps_number': 0,
                    'apps_percent': 0,
                    'documentation': ['http://example.com/doc']
                },
            ],
            'application': {
                'id': app.id,
                'handle': app.handle,
                'name': app.name,
                'creator': '',
                'downloads': '',
                'version': app.version,
                'version_code': app.version_code,
                'icon_path': '',
                'app_uid': '',
                'icon_phash': '',
                'report': report.id,
                'source': app.source,
            }
        }
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)


class RestfulApiTrackersCountTests(APITestCase):
    PATH = '/api/trackers/count'

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_zero_when_no_trackers(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_returns_two_when_two_trackers(self):
        Tracker.objects.create(
            name='Teemo',
            description='bad tracker',
            code_signature='com.teemo',
            network_signature='teemo.com',
            website='https://www.example.com'
        )

        Tracker.objects.create(
            name='Google Ads',
            description='bad tracker #2',
            code_signature='com.google.ads',
            network_signature='google.com',
            website='https://www.example.com'
        )

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)


class RestfulApiReportsCountTests(APITestCase):
    PATH = '/api/reports/count'

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_zero_when_no_reports(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_returns_two_when_two_reports(self):
        Report.objects.create(id=1234)
        Report.objects.create(id=1235)

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)


class RestfulApiApplicationsCountTests(APITestCase):
    PATH = '/api/applications/count'

    def _force_authentication(self):
        user = User.objects.create_user('username', 'Pas$w0rd')
        self.client.force_authenticate(user)

    def test_returns_unauthorized_when_no_auth(self):
        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, 401)

    def test_returns_zero_when_no_applications(self):
        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_returns_one_when_one_application(self):
        report = Report.objects.create(id=1234)
        Application.objects.create(
            name='app_name',
            handle='handle',
            source='google',
            report=report
        )

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_returns_two_when_two_distinct_applications(self):
        report1 = Report.objects.create(id=1234)
        Application.objects.create(
            name='app_name1',
            handle='handle1',
            source='google',
            report=report1
        )
        report2 = Report.objects.create(id=1235)
        Application.objects.create(
            name='app_name2',
            handle='handle2',
            source='google',
            report=report2
        )
        report3 = Report.objects.create(id=1236)
        Application.objects.create(
            name='app_name1',
            handle='handle1',
            source='google',
            report=report3
        )

        self._force_authentication()
        response = self.client.get(self.PATH)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
