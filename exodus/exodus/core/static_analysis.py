# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from gpapi.googleplay import GooglePlayAPI, RequestError
from minio.error import (ResponseError)

from exodus_core.analysis.static_analysis import StaticAnalysis as CoreSA
from trackers.models import Tracker


class StaticAnalysis(CoreSA):
    def __init__(self, apk_path=None):
        super().__init__(apk_path)

    def load_trackers_signatures(self):
        """
        Load trackers signatures from database.
        """
        self.signatures = Tracker.objects.order_by('name')
        self._compile_signatures()

    def get_icon_and_phash(self, storage, icon_name):
        """
        Get the application icon, save it to Minio and get its perceptual hash
        :param storage: minio storage helper
        :param icon_name: file name for the icon
        :return: icon name and phash if success, otherwise empty strings
        """
        with NamedTemporaryFile() as f:
            icon_path = self.save_icon(f.name)
            if icon_path is None:
                return ('', '')

            try:
                storage.put_file(f.name, icon_name)
            except ResponseError as err:
                logging.info(err)
                icon_name = ''

            icon_phash = self.get_phash(f.name)

            return (icon_name, icon_phash)

    def get_app_info(self):
        """
        Get the application information like creator, number of downloads, etc.
        :return: app info dictionary if available, None otherwise
        """
        app_details = self.get_application_details()
        if app_details is None:
            return None

        info = {
            'title': app_details.get('title'),
            'creator': app_details.get('author'),
            'size': app_details.get('installationSize'),
            'downloads': app_details.get('numDownloads'),
            'update': app_details.get('uploadDate'),
            'handle': app_details.get('docId'),
            'version': app_details.get('versionCode'),
            'rating': 'unknown',
        }
        return info


def download_apk(storage, handle, tmp_dir, apk_name, apk_tmp):
    """
    Download the APK from Google Play for the given handle.
    :param storage: minio storage helper
    :param handle: application handle to download
    :param tmp_dir: directory to save the APK in
    :param apk_name: name of the APK in Minio storage
    :param apk_tmp: apk temporary name
    :return: True if succeed, False otherwise
    """
    DEVICE_CODE_NAMES = [
        'default',
        'bacon',
        'hammerhead',
        'manta',
        'cloudbook',
        'bullhead'
    ]

    for device in DEVICE_CODE_NAMES:
        logging.info("Download with device {}".format(device))
        try:
            if device == 'default':
                api = GooglePlayAPI()
            else:
                api = GooglePlayAPI(device_codename=device)
            api.login(
                email=settings.GOOGLE_ACCOUNT_USERNAME,
                password=settings.GOOGLE_ACCOUNT_PASSWORD
            )

            if not os.path.exists(tmp_dir):
                os.mkdir(tmp_dir)
            download = api.download(handle)

            with open(apk_tmp, 'wb') as first:
                for chunk in download.get('file').get('data'):
                    first.write(chunk)
        except RequestError as e:
            logging.warning(e)
            continue
        except Exception as e:
            logging.error(e)
            break

        apk = Path(apk_tmp)
        if apk.is_file():
            try:
                storage.put_file(apk_tmp, apk_name)
                return True
            except ResponseError as err:
                logging.error(err)
                return False

    logging.error("Could not download '{}'".format(handle))
    return False


def clear_analysis_files(storage, tmp_dir, bucket, remove_from_storage=False):
    """
    Clear the analysis files (local + on Minio storage).
    :param storage: Minio storage helper
    :param tmp_dir: local temporary dir to remove
    :param bucket: Minio object prefix to remove
    :param remove_from_storage: remove objects in Minio if set to True
    """
    logging.info('Removing %s' % tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    if remove_from_storage:
        storage.clear_prefix(bucket)
