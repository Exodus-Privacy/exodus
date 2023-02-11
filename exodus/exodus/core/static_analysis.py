# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import logging
import os
import subprocess
import requests
import shutil
import xml.etree.ElementTree as ET
import zipfile
from bs4 import BeautifulSoup
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from google_play_scraper import app as google_app
from minio.error import (ResponseError)

from exodus_core.analysis.static_analysis import StaticAnalysis as CoreSA
from exodus.core.storage import RemoteStorageHelper
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

    def get_icon_and_phash(self, storage, icon_name, source):
        """
        Get the application icon, save it to Minio and get its perceptual hash
        :param storage: minio storage helper
        :param icon_name: file name for the icon
        :param icon_name: source of the app (ex: google, fdroid)
        :return: icon phash if success, otherwise None
        """
        with NamedTemporaryFile() as f:
            icon_path = self.save_icon(f.name)
            if not icon_path:
                logging.warning('Downloading icon from store website')
                try:
                    get_icon_from_store(self.get_package(), source, f.name)
                    logging.debug('Icon downloaded from {}'.format(source))
                except Exception as e:
                    logging.error(e)
                    return None

            try:
                storage.put_file(f.name, icon_name)
            except ResponseError as err:
                logging.info(err)
                return None

            icon_phash = self.get_phash(f.name)

            return icon_phash

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


def is_paid_app(handle):
    try:
        google_play_data = google_app(
            handle,
            lang='en',  # defaults to 'en'
            country='us'  # defaults to 'us'
        )
        return (google_play_data.get('free') is False)
    except Exception as e:
        logging.warning("Impossible to get Google Play data")
        logging.warning(e)
        return False


def download_apk(storage, handle, params):
    ret = False
    logging.info("Will download {}".format(handle))
    if params.source == "google":
        logging.info("Download from Google Play store")
        ret = download_google_apk(storage, handle, params.tmp_dir, params.apk_name, params.apk_tmp, params.source)

        if not ret:
            params.source = "apkpure"
            logging.info("Download from APKPure")
            ret = download_google_apk(storage, handle, params.tmp_dir, params.apk_name, params.apk_tmp, params.source)

    elif params.source == "fdroid":
        logging.info("Download from F-Droid")
        ret = download_fdroid_apk(storage, handle, params.tmp_dir, params.apk_name, params.apk_tmp)
    return ret


def _get_fdroid_app_data(handle):
    with NamedTemporaryFile() as f:
        storage_helper = RemoteStorageHelper()
        try:
            storage_helper.get_file('fdroid_index.xml', f.name)
            tree = ET.parse(f.name)
        except Exception:
            raise Exception("Could not get Fdroid index from Minio")

    root = tree.getroot()
    for child in root:
        if child.tag != 'repo':
            if child.attrib['id'] == handle:
                return child

    return None


def _get_fdroid_localized_data(handle):
    with NamedTemporaryFile() as f:
        storage_helper = RemoteStorageHelper()
        try:
            storage_helper.get_file('fdroid_index_v1.json', f.name)
            f = open(f.name)
            fdroid_data = json.load(f)
        except Exception:
            raise Exception("Could not get Fdroid index from Minio")

    for app in fdroid_data['apps']:
        if app['packageName'] == handle:
            return app['localized']['en-US']

    return None


def download_fdroid_apk(storage, handle, tmp_dir, apk_name, apk_tmp):
    """
    Download the APK from F-Droid for the given handle.
    :param storage: minio storage helper
    :param handle: application handle to download
    :param tmp_dir: directory to save the APK in
    :param apk_name: name of the APK in Minio storage
    :param apk_tmp: apk temporary name
    :return: True if succeed, False otherwise
    """
    url = ''
    data = _get_fdroid_app_data(handle)
    if not data:
        return False

    for package in data.findall('package'):
        url = '{}/{}'.format(settings.FDROID_MIRROR, package.find('apkname').text)
        break

    if not url:
        return False

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    try:
        r = requests.get(url)
        open(apk_tmp, 'wb').write(r.content)
    except Exception:
        return False

    apk = Path(apk_tmp)
    if apk.is_file():
        try:
            storage.put_file(apk_tmp, apk_name)
            return True
        except ResponseError as err:
            logging.error(err)
            return False
    else:
        return False


def extract_apk_from_xapk(apk_tmp, tmp_dir):
    xapk_file_path = apk_tmp.replace(".apk", ".xapk")
    xapk_file = Path(xapk_file_path)

    if xapk_file.is_file():
        logging.info("Extraction apk from xapk")
        with zipfile.ZipFile(xapk_file_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)


def download_google_apk(storage, handle, tmp_dir, apk_name, apk_tmp, source):
    """
    Download the APK from Google Play for the given handle.
    :param storage: minio storage helper
    :param handle: application handle to download
    :param tmp_dir: directory to save the APK in
    :param apk_name: name of the APK in Minio storage
    :param apk_tmp: apk temporary name
    :return: True if succeed, False otherwise
    """
    try:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        download_with_apkeep(source, handle, tmp_dir)

    except Exception as e:
        logging.error(e)
        return False

    apk = Path(apk_tmp)
    if source == "apkpure":
        try:
            extract_apk_from_xapk(apk_tmp, tmp_dir)
        except Exception as e:
            logging.error(e)
            return False

    if apk.is_file():
        try:
            storage.put_file(apk_tmp, apk_name)
            return True
        except ResponseError as err:
            logging.error(err)
            return False

    return False


def download_with_apkeep(source, handle, tmp_dir):
    if source == "google":
        subprocess.run([
            "apkeep",
            "-d",
            "google-play",
            "-a",
            handle,
            "-u",
            settings.GOOGLE_ACCOUNT_USERNAME,
            "-p",
            settings.GOOGLE_ACCOUNT_PASSWORD,
            "-o",
            "device=walleye",
            tmp_dir
        ], env=os.environ.copy())

    elif source == "apkpure":
        subprocess.run([
            "apkeep",
            "-d",
            "apk-pure",
            "-a",
            handle,
            "-o",
            "device=walleye",
            tmp_dir
        ])


def get_icon_from_store(handle, source, dest):
    if source == "fdroid":
        get_icon_from_fdroid(handle, dest)
    else:
        get_icon_from_gplay(handle, dest)


def get_icon_from_fdroid(handle, dest):
    """
    Download the application icon from F-Droid website
    :param handle: application handle
    :param dest: file to be saved
    :raises Exception: if unable to download icon
    """
    icon_url = get_icon_url_fdroid(handle)
    f = requests.get(icon_url)
    with open(dest, mode='wb') as fp:
        fp.write(f.content)
    if not os.path.isfile(dest) or os.path.getsize(dest) == 0:
        raise Exception('Unable to download the icon from fdroid')


def get_icon_url_fdroid(handle):
    try:
        data = _get_fdroid_app_data(handle)
        icon = data.find('icon').text
        icon_url = 'https://f-droid.org/repo/icons-640/{}'.format(icon)
    except Exception:
        # https://gitlab.com/fdroid/fdroiddata/-/issues/2436
        logging.warning('Trying to find icon in localized metadata')
        try:
            data = _get_fdroid_localized_data(handle)
            icon_url = 'https://f-droid.org/repo/{}/en-US/{}'.format(handle, data['icon'])
        except Exception:
            logging.warning('Trying to find icon from f-droid website')
            address = 'https://f-droid.org/en/packages/%s' % handle
            page_content = requests.get(address).text
            soup = BeautifulSoup(page_content, 'html.parser')
            icon_images = soup.find_all('img', {'class': 'package-icon'})
            if len(icon_images) == 0:
                raise Exception('Unable to get icon url from fdroid')
            icon_url = '{}'.format(icon_images[0]['src'])
            if not icon_url.startswith('http'):
                icon_url = 'https://f-droid.org{}'.format(icon_url)
    return icon_url


def get_icon_from_gplay(handle, dest):
    """
    Download the application icon from Google Play website
    :param handle: application handle
    :param dest: file to be saved
    :raises Exception: if unable to download icon
    """

    # TODO: refactor with function is_paid_app to make the call only once
    google_play_data = google_app(
        handle,
        lang='en',  # defaults to 'en'
        country='us'  # defaults to 'us'
    )

    if icon_url := google_play_data.get('icon'):
        f = requests.get(icon_url)
        with open(dest, mode='wb') as fp:
            fp.write(f.content)
        if os.path.isfile(dest) and os.path.getsize(dest) > 0:
            return

    raise Exception('Unable to download the icon from GPlay')


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
