# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import tempfile
import tracemalloc
import gc
from analysis_query.models import *
from reports.models import Report, Application, Apk, Permission, NetworkAnalysis
from .celery import app
from .static_analysis import *


@app.task(bind = True)
def start_static_analysis(self, analysis):
    """
    Compute the entire static analysis
    :param self: celery task
    :param analysis: a StaticAnalysis instance
    """
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    request = AnalysisRequest.objects.get(pk = analysis.query.id)
    request.description = 'Your request is running'
    request.save()
    dl_r = download_apk(request.handle, analysis.tmp_dir, analysis.apk_name, analysis.apk_tmp)
    if not dl_r:
        # Unable to download the APK
        clear_analysis_files(analysis.tmp_dir, analysis.bucket, True)
        request.in_error = True
        request.description = 'Unable to download the APK'
        request.processed = True
        request.save()

        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        print("[ Top 10 differences - on error 1 ]")
        for stat in top_stats[:10]:
            print(stat)

        return -1

    request.description = 'Download APK: success'
    request.save()

    if not decode_apk_file(analysis.apk_tmp, analysis.decoded_dir):
        # Unable to decode the APK
        clear_analysis_files(analysis.tmp_dir, analysis.bucket, True)
        request.in_error = True
        request.description = 'Unable to decode the APK'
        request.processed = True
        request.save()

        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        print("[ Top 10 differences - on error 2 ]")
        for stat in top_stats[:10]:
            print(stat)

        return -1

    request.description = 'Decode APK: success'
    request.save()

    local_class_list_file = list_embedded_classes(analysis.decoded_dir, analysis.class_list_file)

    if local_class_list_file == '':
        # Unable to compute the class list
        clear_analysis_files(analysis.tmp_dir, analysis.bucket, True)
        request.in_error = True
        request.description = 'Unable to compute the class list'
        request.processed = True
        request.save()

        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        print("[ Top 10 differences - on error 3 ]")
        for stat in top_stats[:10]:
            print(stat)

        return -1

    request.description = 'List embedded classes: success'
    request.save()

    shasum = get_sha256sum(analysis.apk_tmp)
    version = get_application_version(analysis.decoded_dir)
    handle = get_application_handle(analysis.decoded_dir)
    perms = get_application_permissions(analysis.decoded_dir)
    icon_file = get_application_icon(analysis.icon_name, request.handle)
    app_info = get_application_details(request.handle)
    version_code = get_application_version_code(analysis.decoded_dir)

    request.description = 'Get application details: success'
    request.save()

    # Find trackers
    trackers = find_embedded_trackers(local_class_list_file)

    request.description = 'Tracker analysis: success'
    request.save()

    # If a report exists for this couple (handle, version), just return it
    existing_report = Report.objects.filter(application__handle = handle, application__version = version).order_by(
        '-creation_date').first()
    if existing_report is not None:
        clear_analysis_files(analysis.tmp_dir, analysis.bucket, True)
        request.description = 'A report already exists for this application version'
        request.processed = True
        request.report_id = existing_report.id
        request.save()

        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        print("[ Top 10 differences - on existing report ]")
        for stat in top_stats[:10]:
            print(stat)

        return existing_report.id

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

    for perm in perms:
        p = Permission(application = app)
        p.name = perm
        p.save(force_insert = True)

    report.found_trackers = trackers
    report.save()

    clear_analysis_files(analysis.tmp_dir, analysis.bucket, False)
    request.description = 'Static analysis complete'
    request.processed = True
    request.report_id = report.id
    request.save()

    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    print("[ Top 10 differences - on success ]")
    for stat in top_stats[:10]:
        print(stat)

    return report.id


class StaticAnalysis:
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
