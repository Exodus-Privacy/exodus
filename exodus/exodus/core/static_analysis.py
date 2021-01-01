# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import requests
import shutil
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from gpapi.googleplay import GooglePlayAPI, RequestError
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


def download_apk(storage, handle, tmp_dir, apk_name, apk_tmp, source="google"):
    ret = False
    logging.info("Will download {}".format(handle))
    if source == "google":
        logging.info("Download from gplay")
        ret = download_google_apk(storage, handle, tmp_dir, apk_name, apk_tmp)
    elif source == "fdroid":
        logging.info("Download from F-Droid")
        ret = download_fdroid_apk(storage, handle, tmp_dir, apk_name, apk_tmp)
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


def download_google_apk(storage, handle, tmp_dir, apk_name, apk_tmp):
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
        'walleye',  # Google Pixel 2 (2017)
        't00q',  # Asus Zenfone 4 (2017)
        'bullhead',  # Nexus 5X (2015)
        'bacon',  # OnePlus One (2014)
        'manta',  # Nexus 10 (2012)
        'cloudbook',  # Acer Aspire One Cloudbook (2015)
        'hero2lte',  # Samsung Galaxy S7 Edge (2016)
        'gtp7510',  # Samsung Galaxy Tab 10.1 (2011)
        'sloane',  # Amazon Fire TV 2 (2018?)
        'BRAVIA_ATV2'  # Sony Bravia 4K GB (2016)
    ]

    for device in DEVICE_CODE_NAMES:
        logging.info("Download with device {}".format(device))
        try:
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

    return False


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
    data = _get_fdroid_app_data(handle)
    if not data:
        raise Exception('Unable to download the icon from fdroid')

    icon = data.find('icon').text
    icon_url = 'https://f-droid.org/repo/icons-640/{}'.format(icon)

    f = requests.get(icon_url)
    with open(dest, mode='wb') as fp:
        fp.write(f.content)
    if not os.path.isfile(dest) or os.path.getsize(dest) == 0:
        raise Exception('Unable to download the icon from fdroid')


def get_icon_from_gplay(handle, dest):
    """
    Download the application icon from Google Play website
    :param handle: application handle
    :param dest: file to be saved
    :raises Exception: if unable to download icon
    """
    address = 'https://play.google.com/store/apps/details?id=%s' % handle
    gplay_page_content = requests.get(address).text
    soup = BeautifulSoup(gplay_page_content, 'html.parser')
    icon_images = soup.find_all('img', {'alt': 'Cover art'})
    if len(icon_images) > 0:
        icon_url = '{}'.format(icon_images[0]['src'])
        if not icon_url.startswith('http'):
            icon_url = 'https:{}'.format(icon_url)
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
