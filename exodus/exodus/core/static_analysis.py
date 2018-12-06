# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import requests
import shlex
import shutil
import time
from pathlib import Path
from subprocess import TimeoutExpired
from tempfile import NamedTemporaryFile

from exodus_core.analysis.static_analysis import StaticAnalysis as CoreSA
from future.moves import subprocess
from gplaycli import gplaycli
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

    def get_application_icon(self, storage, icon_name):
        """
        Get the application icon and save it to Minio
        :param storage: minio storage helper
        :param icon_name: file name for the icon
        :return: icon name if success, empty string in case of failure
        """
        with NamedTemporaryFile() as f:
            icon_path = self.save_icon(f.name)
            if icon_path is None:
                return ''
            try:
                storage.put_file(f.name, icon_name)
            except ResponseError as err:
                logging.info(err)
                return ''
            return icon_name


# TODO: remove this class if unused
class ExGPlaycli(gplaycli.GPlaycli):
    def __init__(self):
        gplaycli.GPlaycli.__init__(self)

    def after_download(self, failed_downloads):
        pass

    def retrieve_token(self, force_new=False):
        token, gsfid = self.get_cached_token()
        if token is not None and not force_new:
            logging.info("Using cached token.")
            return token, gsfid
        logging.info("Retrieving token ...")
        r = requests.get(self.token_url)
        if r.text == 'Auth error':
            msg = 'Token dispenser auth error, probably too many connections'
            logging.info(msg)
            raise ConnectionError(msg)
        elif r.text == "Server error":
            msg = 'Token dispenser server error'
            logging.info(msg)
            raise ConnectionError(msg)
        token, gsfid = r.text.split(" ")
        logging.info("Token: %s", token)
        logging.info("GSFId: %s", gsfid)
        self.token = token
        self.gsfid = gsfid
        self.write_cached_token(token, gsfid)
        return token, gsfid


def get_application_details(handle):
    """
    Get the application details like creator, number of downloads, etc.
    :param handle: application handle
    :return: application details dictionary
    """
    TIME_BEFORE_RETRY = 2
    API_SEARCH_LIMIT = 5

    gpc = gplaycli.GPlaycli()
    gpc.token_enable = True
    gpc.token_url = "https://matlink.fr/token/email/gsfid"
    try:
        gpc.token, gpc.gsfid = gpc.retrieve_token(force_new=False)
    except (ConnectionError, ValueError):
        try:
            time.sleep(TIME_BEFORE_RETRY)
            gpc.token, gpc.gsfid = gpc.retrieve_token(force_new=True)
        except (ConnectionError, ValueError):
            return None
    gpc.connect()
    objs = gpc.api.search(handle, API_SEARCH_LIMIT)
    try:
        for obj in objs:
            if obj['docId'] != handle:
                continue
            infos = {
                'title': obj['title'],
                'creator': obj['author'],
                'size': obj['installationSize'],
                'downloads': obj['numDownloads'],
                'update': obj['uploadDate'],
                'handle': obj['docId'],
                'version': obj['versionCode'],
                'rating': 'unknown',
            }
            return infos
    except Exception as e:
        logging.error('Unable to parse applications details')
        logging.error(e)
        return None
    return None


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
        '',
        '',
        '-dc hammerhead',
        '-dc manta',
        '-dc cloudbook',
        '-dc bullhead'
    ]
    MAX_RETRIES = len(DEVICE_CODE_NAMES)

    retry = MAX_RETRIES
    exit_code = 1
    while retry > 0:
        cmd = 'gplaycli -v -a -y -pd %s %s -f %s/' % (
            handle, DEVICE_CODE_NAMES[retry % MAX_RETRIES], tmp_dir)
        try:
            proc = subprocess.Popen(
                shlex.split(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            outs, errs = proc.communicate(timeout=240)
            exit_code = proc.returncode
            if "[ERROR]" in str(errs) or "[ERROR]" in str(outs):
                print(errs.decode("utf-8"))
                raise Exception("Error while downloading apk file")
        except TimeoutExpired:
            exit_code = 1
            break
        except Exception as e:
            logging.info(e)
            exit_code = 1

        apk = Path(apk_tmp)
        if apk.is_file():
            exit_code = 0

        if exit_code == 0:
            break

        # Remove the token only if it failed on the first attempt
        if retry == MAX_RETRIES:
            remove_token()

        retry -= 1
        time.sleep(2)

    # Upload APK in storage
    apk = Path(apk_tmp)
    if exit_code == 0 and apk.is_file():
        try:
            storage.put_file(apk_tmp, apk_name)
        except ResponseError as err:
            logging.info(err)
            return False

    return exit_code == 0


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
