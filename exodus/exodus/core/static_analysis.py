# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import shlex
import shutil
import time
from pathlib import Path
from subprocess import check_output, STDOUT, TimeoutExpired
from tempfile import NamedTemporaryFile

from exodus_core.analysis.static_analysis import StaticAnalysis as CoreSA
from minio.error import (ResponseError)

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


def remove_token():
    token_path = os.path.join(str(Path.home()), '.cache/gplaycli/token')
    if os.path.exists(token_path):
        logging.info("Removing cached token")
        try:
            os.remove(token_path)
        except Exception as e:
            logging.info("Impossible to remove the token: %s", str(e))
    else:
        logging.info("No token found in %s", token_path)


def download_apk(storage, handle, tmp_dir, apk_name, apk_tmp):
    """
    Download the APK from Google Play for the given handle.
    :param storage: minio storage helper
    :param handle: application handle to download
    :param tmp_dir: download destination directory
    :param apk_name: name of the APK in Minio storage
    :param apk_tmp: apk temporary name
    :return: True if succeed, False otherwise
    """
    DEVICE_CODE_NAMES = [
        'bacon',
        'hammerhead',
        'manta',
        'cloudbook',
        'bullhead'
    ]
    RETRY_PER_DEVICE = 3

    refreshed_token = False
    for device in DEVICE_CODE_NAMES:
        cmd = 'gplaycli -v -a -y -pd {} -dc {} -f {}/'.format(
            handle,
            device,
            tmp_dir
        )
        for i in range(RETRY_PER_DEVICE):
            try:
                output = check_output(
                    shlex.split(cmd),
                    stderr=STDOUT,
                    timeout=240  # Timeout of 4 minutes
                )
                output_str = output.decode('utf-8')
                logging.info(output_str)
                if '[ERROR]' in output_str:
                    filtered = output_str.replace('[ERROR] cache file does not exists or is corrupted', '')
                    if '[ERROR]' in filtered:
                        raise RuntimeError('Error while downloading apk file')

                apk = Path(apk_tmp)
                if apk.is_file():
                    try:
                        storage.put_file(apk_tmp, apk_name)
                        return True
                    except ResponseError as err:
                        logging.info(err)
                        return False

            except TimeoutExpired:
                logging.warning("Timeout of gplaycli download command")
                return False
            except Exception as e:
                logging.info(e)

            logging.info("Could not download with device {}".format(device))
            if not refreshed_token:
                remove_token()
                refreshed_token = True
            time.sleep(2)

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
