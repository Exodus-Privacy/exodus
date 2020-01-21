# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import tempfile

from django.utils.translation import gettext_lazy as _

from analysis_query.models import AnalysisRequest
from exodus.core.storage import RemoteStorageHelper
from reports.models import Certificate, Report, Application, Apk, Permission
from .celery import app
from .static_analysis import download_apk, clear_analysis_files, StaticAnalysis

EXIT_CODE = -1


def change_description(request, msg):
    """
    Utility function to change the description message of the analysis request
    :param request: an AnalysisRequest instance
    :param msg: message to set as a description
    """
    request.description = msg
    logging.info(request.description)
    request.save()


def save_error(storage_helper, analysis, request, msg):
    """
    Utility function to clear files and update analysis request object
    :param storage_helper: minio storage helper
    :param analysis: a StaticAnalysis instance
    :param request: an AnalysisRequest instance
    :param msg: message to set as a description
    """
    clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, True)
    request.description = msg
    request.in_error = True
    request.processed = True
    request.save()


@app.task(ignore_result=True)
def start_static_analysis(analysis):
    """
    Compute the entire static analysis
    :param analysis: a StaticAnalysis instance
    """
    request = AnalysisRequest.objects.get(pk=analysis.query.id)
    request.description = _('Your request is running')
    request.save()
    storage_helper = RemoteStorageHelper(analysis.bucket)

    if request.apk:
        with open(analysis.apk_tmp, 'wb') as out:
            out.write(request.apk.read())
        storage_helper.put_file(analysis.apk_tmp, analysis.apk_name)
        request.apk.delete()
    else:
        # Download APK and put it on Minio storage
        dl_r = download_apk(storage_helper, request.handle, analysis.tmp_dir, analysis.apk_name, analysis.apk_tmp)
        if not dl_r:
            msg = _('Unable to download the APK')
            save_error(storage_helper, analysis, request, msg)
            return EXIT_CODE

        change_description(request, _('Download APK: success'))

    # Decode the APK file
    try:
        static_analysis = StaticAnalysis(analysis.apk_tmp)
        static_analysis.load_apk()
    except Exception as e:
        logging.info(e)
        msg = _('Unable to decode the APK')
        save_error(storage_helper, analysis, request, msg)
        return EXIT_CODE

    change_description(request, _('Decode APK: success'))

    # List and save embedded classes
    try:
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            static_analysis.save_embedded_classes_in_file(fp.name)
            storage_helper.put_file(fp.name, analysis.class_list_file)
    except Exception as e:
        logging.info(e)
        msg = _('Unable to compute the class list')
        save_error(storage_helper, analysis, request, msg)
        return EXIT_CODE

    change_description(request, _('List embedded classes: success'))

    # APK
    shasum = static_analysis.get_sha256()

    # Application
    handle = static_analysis.get_package()
    version = static_analysis.get_version()
    version_code = static_analysis.get_version_code()
    app_name = static_analysis.get_app_name()

    # TODO: increase character limit in DB (see #300)
    if len(version) > 50 or len(version_code) > 50 or len(app_name) > 200:
        msg = _('Unable to create the analysis report')
        save_error(storage_helper, analysis, request, msg)
        return EXIT_CODE

    # If a report exists for the same handle, version & version_code, return it
    existing_report = Report.objects.filter(
        application__handle=handle,
        application__version=version,
        application__version_code=version_code
    ).order_by('-creation_date').first()

    if existing_report is not None:
        clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, True)
        request.description = _('A report already exists for this application version')
        request.processed = True
        request.report_id = existing_report.id
        request.save()
        return existing_report.id

    # APK
    try:
        certificates = static_analysis.get_certificates()
    except Exception as e:
        logging.info(e)
        msg = _('Unable to get certificates')
        save_error(storage_helper, analysis, request, msg)
        return EXIT_CODE

    # Fingerprint
    try:
        perms = static_analysis.get_permissions()

        app_uid = static_analysis.get_application_universal_id()
        if len(app_uid) < 16:
            raise Exception('Unable to compute the Universal Application ID')

        icon_file, icon_phash = static_analysis.get_icon_and_phash(storage_helper, analysis.icon_name)
        if len(str(icon_phash)) < 16 and not request.apk:
            raise Exception('Unable to compute the icon perceptual hash')
    except Exception as e:
        logging.info(e)
        msg = _('Unable to compute APK fingerprint')
        save_error(storage_helper, analysis, request, msg)
        return EXIT_CODE

    # Application details
    try:
        app_info = static_analysis.get_app_info()
    except Exception as e:
        logging.info(e)
        msg = _('Unable to get application details from Google Play')
        save_error(storage_helper, analysis, request, msg)
        return EXIT_CODE

    change_description(request, _('Get application details: success'))

    # Find trackers
    trackers = static_analysis.detect_trackers()

    change_description(request, _('Tracker analysis: success'))

    report = Report(
        apk_file=analysis.apk_name,
        storage_path='',
        bucket=request.bucket,
        class_list_file=analysis.class_list_file
    )
    report.save()

    app = Application(
        report=report,
        handle=handle,
        version=version,
        version_code=version_code,
        name=app_name,
        icon_phash=icon_phash,
        app_uid=app_uid
    )
    if app_info is not None:
        app.name = app_info['title']
        app.creator = app_info['creator']
        app.downloads = app_info['downloads']
    if icon_file != '':
        app.icon_path = analysis.icon_name
    app.save(force_insert=True)

    apk = Apk(
        application=app,
        name=analysis.apk_name,
        sum=shasum
    )
    apk.save(force_insert=True)

    for certificate in certificates:
        c = Certificate(
            apk=apk,
            issuer=certificate.issuer,
            fingerprint=certificate.fingerprint,
            subject=certificate.subject,
            serial_number=certificate.serial
        )
        c.save(force_insert=True)

    for perm in perms:
        p = Permission(
            application=app,
            name=perm
        )
        p.save(force_insert=True)

    report.found_trackers.set(trackers)

    change_description(request, _('Static analysis complete'))
    clear_analysis_files(storage_helper, analysis.tmp_dir, analysis.bucket, False)
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
