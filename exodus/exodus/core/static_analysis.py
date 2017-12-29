# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import re
import shlex
import shutil
import time
from hashlib import sha256
from pathlib import Path

from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
from future.moves import subprocess
from minio.error import (ResponseError)

from trackers.models import Tracker


class StaticAnalysis:
    def __init__(self, apk_path = None):
        self.apk = None
        self.decoded = None
        self.apk_path = apk_path
        self.signatures = None
        if apk_path is not None:
            self.load_apk()

    def load_trackers_signatures(self):
        """
        Load trackers signatures from database.
        """
        self.signatures = Tracker.objects.order_by('name')

    def load_apk(self):
        """
        Load the APK file.
        """
        if self.apk is None:
            self.apk = APK(self.apk_path)

    def decode_apk(self):
        """
        Decode the APK file.
        """
        if self.apk is None:
            self.load_apk()
        if self.decoded is None:
            self.decoded = DalvikVMFormat(self.apk)

    def detect_trackers_in_list(self, class_list):
        """
        Detect embedded trackers in the provided classes list.
        :return: list of embedded trackers
        """
        trackers = []
        if self.signatures is None:
            self.load_trackers_signatures()
        for tracker in self.signatures:
            if len(tracker.code_signature) > 3:
                for clazz in class_list:
                    m = re.search(tracker.code_signature, clazz)
                    if m is not None:
                        trackers.append(tracker)
                        break
        return trackers

    def detect_trackers(self, class_list_file = None):
        """
        Detect embedded trackers.
        :return: list of embedded trackers
        """
        if self.signatures is None:
            self.load_trackers_signatures()
        if class_list_file is None:
            if self.signatures is None:
                self.load_trackers_signatures()
            if self.decoded is None:
                self.decode_apk()
            return self.detect_trackers_in_list(self.get_embedded_classes())
        else:
            with open(class_list_file, 'r') as classes_file:
                classes = classes_file.readlines()
                return self.detect_trackers_in_list(classes)

    def get_embedded_classes(self):
        """
        List embedded Java classes
        :return: list of Java classes
        """
        if self.decoded is None:
            self.decode_apk()
        return self.decoded.get_classes_names()

    def save_embedded_classes_in_file(self, file_path):
        """
        Save list of embedded classes in file.
        :param file_path: file to write
        """
        with open(file_path, 'w+') as f:
            f.write('\n'.join(self.get_embedded_classes()))

    def get_version(self):
        """
        Get the application version name
        :return: version name
        """
        return self.apk.get_androidversion_name()

    def get_version_code(self):
        """
        Get the application version code
        :return: version code
        """
        return self.apk.get_androidversion_code()

    def get_permissions(self):
        """
        Get application permissions
        :return: application permissions list
        """
        return self.apk.get_permissions()

    def get_app_name(self):
        """
        Get application name
        :return: application name
        """
        return self.apk.get_app_name()

    def get_package(self):
        """
        Get application package
        :return: application package
        """
        return self.apk.get_package()

    def get_libraries(self):
        """
        Get application libraries
        :return: application libraries list
        """
        return self.apk.get_libraries()

    def get_sha256(self):
        """
        Get the sha256sum of the APK file
        :return: hex sha256sum
        """
        BLOCKSIZE = 65536
        hasher = sha256()
        with open(self.apk_path, 'rb') as apk:
            buf = apk.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = apk.read(BLOCKSIZE)
        return hasher.hexdigest()


from gplaycli import gplaycli
import requests


class ExGPlaycli(gplaycli.GPlaycli):
    def __init__(self):
        gplaycli.GPlaycli.__init__(self)

    def after_download(self, failed_downloads):
        pass

    def retrieve_token(self, force_new = False):
        token, gsfid = self.get_cached_token()
        if token is not None and not force_new:
            logging.info("Using cached token.")
            return token, gsfid
            logging.info("Retrieving token ...")
        r = requests.get(self.token_url)
        if r.text == 'Auth error':
            logging.info('Token dispenser auth error, probably too many connections')
            raise ConnectionError('Token dispenser auth error, probably too many connections')
        elif r.text == "Server error":
            logging.info('Token dispenser server error')
            raise ConnectionError('Token dispenser server error')
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
    # Fix#12 - We have to remove the cached token :S
    shutil.rmtree(os.path.join(str(Path.home()), '.cache/gplaycli/'), ignore_errors = True)

    gpc = gplaycli.GPlaycli()
    gpc.token_enable = True
    gpc.token_url = "https://matlink.fr/token/email/gsfid"
    try:
        gpc.token, gpc.gsfid = gpc.retrieve_token(force_new = False)
    except ConnectionError:
        try:
            time.sleep(2)
            gpc.token, gpc.gsfid = gpc.retrieve_token(force_new = False)
        except ConnectionError:
            return None
    success, error = gpc.connect_to_googleplay_api()
    if error is not None:
        return None
    results = gpc.search(list(), handle, 1, True)
    if len(results) == 2:
        infos = {
            'title': results[1][0],
            'creator': results[1][1],
            'size': results[1][2],
            'downloads': results[1][3],
            'update': results[1][4],
            'handle': results[1][5],
            'version': results[1][6],
            'rating': results[1][7],
        }
        if handle in results[1][5]:
            return infos
    return None


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
    device_code_names = ['', '-dc hammerhead', '-dc manta', '-dc cloudbook', '-dc bullhead']
    retry = 5
    exit_code = 1
    # gpc = ExGPlaycli()
    # gpc.token_enable = False
    # gpc.verbose = True
    # gpc.token_url = "https://matlink.fr/token/email/gsfid"
    # try:
    #     gpc.token, gpc.gsfid = gpc.retrieve_token(force_new = False)
    # except ConnectionError:
    #     try:
    #         time.sleep(2)
    #         gpc.token, gpc.gsfid = gpc.retrieve_token(force_new = False)
    #     except ConnectionError:
    #         return None
    # success, error = gpc.connect_to_googleplay_api()
    # if error is not None:
    #     return False
    while retry != 0:
        # if device_code_names[retry % len(device_code_names)] != '':
        #     gpc.device_codename = device_code_names[retry % len(device_code_names)]
        # gpc.set_download_folder(tmp_dir)
        # gpc.download_packages([handle])
        cmd = 'gplaycli -v -a -t -y -pd %s %s -f %s/' % (handle, device_code_names[retry % len(device_code_names)], tmp_dir)
        try:
            exit_code = subprocess.check_call(shlex.split(cmd), shell = False)
        except:
            exit_code = 1
        apk = Path(apk_tmp)
        if apk.is_file():
            exit_code = 0

        if exit_code == 0:
            break

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


def clear_analysis_files(storage, tmp_dir, bucket, remove_from_storage = False):
    """
    Clear the analysis files (local + on Minio storage).
    :param tmp_dir: local temporary dir to remove
    :param bucket: Minio object prefix to remove
    :param remove_from_storage: remove objects in Minio if set to True
    """
    logging.info('Removing %s' % tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors = True)
    if remove_from_storage:
        storage.clear_prefix(bucket)


def get_application_icon(storage, icon_name, handle, url = None):
    """
    Download the application icon from Google Play.
    :param storage: Minio storage helper
    :param icon_name: icon name in Minio storage
    :param handle: handle of the application
    :param url: force to use the given URL for downloading the icon
    :return: icon name if succeed, empty string otherwise
    """
    from bs4 import BeautifulSoup
    import urllib.request

    if url is None:
        try:
            address = 'https://play.google.com/store/apps/details?id=%s' % handle
            text = urllib.request.urlopen(address).read()
            soup = BeautifulSoup(text, 'html.parser')
            i = soup.find_all('img', {'class': 'cover-image', 'alt': 'Cover art'})
            if len(i) > 0:
                url = '%s' % i[0]['src']
                if not url.startswith('http'):
                    url = 'https:%s' % url
            else:
                return ''
        except Exception:
            return ''

    return storage.download_and_put(url, icon_name)
