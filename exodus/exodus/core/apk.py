# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import tempfile
import os

from django.utils.translation import gettext_lazy as _

from analysis_query.models import *
from exodus.core.storage import RemoteStorageHelper
from reports.models import Report, Application, Apk, Permission, NetworkAnalysis
from .celery import app
from .static_analysis import *


@app.task(ignore_result = True)
def start_static_analysis(analysis):
    """
    Compute the entire static analysis
    :param analysis: a StaticAnalysis instance
    """
    request = AnalysisRequest.objects.get(pk = analysis.query.id)
    request.description = _('Your request is running')
    request.save()
    storage_helper = RemoteStorageHelper(analysis.bucket)

    # Download APK and put it on Minio storage
    dl_r = download_apk(storage_helper, request.handle, analysis.tmp_dir, analysis.apk_name, analysis.apk_tmp)
    if not dl_r:
        # Unable to download the APK
        clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, True)
        request.in_error = True
        request.description = _('Unable to download the APK')
        request.processed = True
        request.save()
        return -1

    request.description = _('Download APK: success')
    logging.info(request.description)
    request.save()

    # Decode the APK file
    try:
        static_analysis = StaticAnalysis(analysis.apk_tmp)
        static_analysis.load_apk()
    except Exception as e:
        print(e)
        # Unable to decode the APK
        clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, True)
        request.in_error = True
        request.description = _('Unable to decode the APK')
        request.processed = True
        request.save()
        return -1

    request.description = _('Decode APK: success')
    logging.info(request.description)
    request.save()

    # List and save embedded classes
    try:
        with tempfile.NamedTemporaryFile(delete = True) as fp:
            static_analysis.save_embedded_classes_in_file(fp.name)
            storage_helper.put_file(fp.name, analysis.class_list_file)
    except Exception as e:
        logging.info(e)
        # Unable to compute the class list
        clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, True)
        request.in_error = True
        request.description = _('Unable to compute the class list')
        request.processed = True
        request.save()
        return -1

    request.description = _('List embedded classes: success')
    logging.info(request.description)
    request.save()

    # APK
    shasum = static_analysis.get_sha256()

    # Application
    handle = static_analysis.get_package()
    version = static_analysis.get_version()
    version_code = static_analysis.get_version_code()

    # If a report exists for this couple (handle, version), just return it
    existing_report = Report.objects.filter(application__handle = handle, application__version = version).order_by(
        '-creation_date').first()
    if existing_report is not None:
        clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, True)
        request.description = _('A report already exists for this application version')
        request.processed = True
        request.report_id = existing_report.id
        request.save()
        return existing_report.id

    # Application
    perms = static_analysis.get_permissions()
    app_uid = static_analysis.get_application_universal_id()
    # icon_file = get_application_icon(storage_helper, analysis.icon_name, request.handle)
    icon_file = static_analysis.get_application_icon(storage_helper, analysis.icon_name)
    icon_phash = static_analysis.get_icon_phash()

    # APK
    certificates = static_analysis.get_certificates()

    # Application details
    app_info = get_application_details(request.handle)

    request.description = _('Get application details: success')
    logging.info(request.description)
    request.save()

    # Find trackers
    trackers = static_analysis.detect_trackers()

    request.description = _('Tracker analysis: success')
    logging.info(request.description)
    request.save()

    report = Report(apk_file = analysis.apk_name, storage_path = '', bucket = request.bucket)
    report.save()
    net_analysis = NetworkAnalysis(report = report)
    net_analysis.save()
    report.class_list_file = analysis.class_list_file
    report.save()
    app = Application(report = report)
    app.handle = handle
    app.version = version
    app.version_code = version_code
    app.name = static_analysis.get_app_name()
    app.icon_phash = icon_phash
    app.app_uid = app_uid
    if app_info is not None:
        app.name = app_info['title']
        app.creator = app_info['creator']
        app.downloads = app_info['downloads']
    if icon_file != '':
        app.icon_path = analysis.icon_name
    app.save(force_insert = True)

    apk = Apk(application = app)
    apk.name = analysis.apk_name
    apk.sum = shasum
    apk.save(force_insert = True)

    for certificate in certificates:
        c = Certificate(apk = apk)
        c.issuer = certificate.issuer
        c.fingerprint = certificate.fingerprint
        c.subject = certificate.subject
        c.serial_number = certificate.serial
        c.save(force_insert = True)

    for perm in perms:
        p = Permission(application = app)
        p.name = perm
        p.save(force_insert = True)

    report.found_trackers = trackers
    report.save()

    clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, False)
    request.description = _('Static analysis complete')
    logging.info(request.description)
    request.processed = True
    request.report_id = report.id
    request.save()
    return report.id


class StaticAnalysisParameters:
    def __init__(self, analysis_query):
        self.query = analysis_query
        self.bucket = analysis_query.bucket
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        self.apk_tool = os.path.join(self.root_dir, "apktool.jar")
        self.tmp_dir = tempfile.mkdtemp()
        self.decoded_dir = os.path.join(self.tmp_dir, 'decoded')
        self.apk_tmp = os.path.join(self.tmp_dir, '%s.apk' % self.query.handle)
        self.apk_name = '%s_%s.apk' % (self.bucket, self.query.handle)
        self.icon_name = '%s_%s.png' % (self.bucket, self.query.handle)
        self.class_list_file = '%s_%s.clist' % (self.bucket, self.query.handle)
