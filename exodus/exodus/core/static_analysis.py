# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import shutil
import subprocess as sp
import time
from pathlib import Path
from xml.dom import minidom

import yaml
from django.conf import settings
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists)

from trackers.models import Tracker


def grep(file, pattern):
    """
    Find the given pattern in the given file.
    :param file: path to file to check
    :param pattern: pattern to find in the file
    :return: True if the pattern has been found in the file, False otherwise.
    """
    cmd = '/bin/grep -q -E "%s" %s' % (pattern, file)
    process = sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    print(exitCode)
    return exitCode == 0


def download_and_put(url, destination_name):
    """
    Download a file and put it on Minio storage.
    :param url: URL of the file to download
    :param destination_name: file name in Minio storage
    :return: the destination name if succeed, empty string otherwise
    """
    import urllib.request, tempfile
    try:
        f = urllib.request.urlopen(url)
        print("Downloading " + url)
        with tempfile.NamedTemporaryFile(delete = True) as fp:
            fp.write(f.read())
            # Upload icon in storage
            minio_client = Minio(settings.MINIO_URL,
                                 access_key = settings.MINIO_ACCESS_KEY,
                                 secret_key = settings.MINIO_SECRET_KEY,
                                 secure = settings.MINIO_SECURE)
            try:
                minio_client.fput_object(settings.MINIO_BUCKET, destination_name, fp.name)
            except ResponseError as err:
                print(err)
            return destination_name
    except Exception as e:
        print(e)
        return ''


def get_application_icon(icon_name, handle, url = None):
    """
    Download the application icon from Google Play.
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

    return download_and_put(url, icon_name)


def find_embedded_trackers(class_list_file):
    """
    Find tracker signatures in the given file.
    :param class_list_file: file containing the list of embedded classes
    :return: array of found trackers
    """
    trackers = Tracker.objects.order_by('name')
    found = []
    for t in trackers:
        if len(t.code_signature) > 3:
            if grep(class_list_file, t.code_signature):
                found.append(t)
    return found


def get_application_version_code(decoded_dir):
    """
    Get the application version code from a decoded APK.
    :param decoded_dir: path to the decoded APK
    :return: version code if found, empty string otherwise
    """
    yml = os.path.join(decoded_dir, 'apktool.yml')
    yml_new = os.path.join(decoded_dir, 'apktool.yml.new')
    cmd = '/bin/cat %s | /bin/grep -v "\!\!" > %s' % (yml, yml_new)
    process = sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode != 0:
        return ''
    with open(yml_new) as f:
        dataMap = yaml.safe_load(f)
        return dataMap['versionInfo']['versionCode']


def get_application_version(decoded_dir):
    """
    Get the application version from a decoded APK.
    :param decoded_dir: path to the decoded APK
    :return: version if found, empty string otherwise
    """
    yml = os.path.join(decoded_dir, 'apktool.yml')
    yml_new = os.path.join(decoded_dir, 'apktool.yml.new')
    cmd = '/bin/cat %s | /bin/grep -v "\!\!" > %s' % (yml, yml_new)
    process = sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode != 0:
        return ''
    with open(yml_new) as f:
        dataMap = yaml.safe_load(f)
        return dataMap['versionInfo']['versionName']


def get_application_handle(decoded_dir):
    """
    Get the application handle from a decoded APK.
    :param decoded_dir: path to the decoded APK
    :return: handle
    """
    xmldoc = minidom.parse(os.path.join(decoded_dir, 'AndroidManifest.xml'))
    man = xmldoc.getElementsByTagName('manifest')[0]
    return man.getAttribute('package')


def get_application_permissions(decoded_dir):
    """
    Get the application permissions from a decoded APK.
    :param decoded_dir: path to the decoded APK
    :return: array of permissions (strings)
    """
    xmldoc = minidom.parse(os.path.join(decoded_dir, 'AndroidManifest.xml'))
    permissions = xmldoc.getElementsByTagName('uses-permission')
    perms = []
    for perm in permissions:
        perms.append(perm.getAttribute('android:name'))
    return perms


def get_sha256sum(apk_path):
    """
    Compute the sha256sum of the given APK.
    :param apk_path: path to the APK file
    :return: sha256 sum
    """
    cmd = '/usr/bin/sha256sum %s | head -c 64' % apk_path
    process = sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    return process.stdout.read()


def decode_apk_file(apk_path, decoded_dir):
    """
    Decode the given APK to the given directory.
    :param apk_path: path to the APK
    :param decoded_dir: path to the target directory
    :return: True if succeed, False otherwise
    """
    root_dir = os.path.dirname(os.path.realpath(__file__))
    apktool = os.path.join(root_dir, "apktool.jar")
    cmd = '/usr/bin/java -jar %s d %s -s -o %s/' % (apktool, apk_path, decoded_dir)
    process = sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    return exitCode == 0


def list_embedded_classes(decoded_dir, class_list_file):
    """
    List embedded Java classes into the given file and put in into Minio storage.
    :param decoded_dir: path to the decoded APK
    :param class_list_file: file in which to put the class list
    :return: name of the class list file if succeed, empty string otherwise
    """
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dexdump = os.path.join(root_dir, "dexdump")
    list_file = '%s/class_list.txt' % decoded_dir
    cmd = '%s %s/classes*.dex > %s; head %s' % (dexdump, decoded_dir, list_file, list_file)
    process = sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode == 0:
        # Upload class list file
        minio_client = Minio(settings.MINIO_URL,
                             access_key = settings.MINIO_ACCESS_KEY,
                             secret_key = settings.MINIO_SECRET_KEY,
                             secure = settings.MINIO_SECURE)
        try:
            minio_client.fput_object(settings.MINIO_BUCKET, class_list_file, list_file)
        except ResponseError as err:
            print(err)
            return ''
        return list_file
    return ''


def get_application_details(handle):
    """
    Get the application details like creator, number of downloads, etc.
    :param handle: application handle
    :return: application details dictionary
    """
    # Fix#12 - We have to remove the cached token :S
    shutil.rmtree(os.path.join(str(Path.home()), '.cache/gplaycli/'), ignore_errors = True)
    cmd = 'gplaycli -t -s %s -n 1' % handle
    lines = []
    with sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT, universal_newlines = True) as p:
        for line in iter(p.stdout):
            if 'Traceback' in line or 'Error' in line:
                return None
            lines.append(line.replace('\n', ''))
        if len(lines) != 2:
            return None
        columns = []
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'title', 'text': 'Title'})
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'creator', 'text': 'Creator'})
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'size', 'text': 'Size'})
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'downloads', 'text': 'Downloads'})
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'update', 'text': 'Last Update'})
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'handle', 'text': 'AppID'})
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'version', 'text': 'Version'})
        columns.append({'start': 0, 'end': 0, 'value': '', 'name': 'rating', 'text': 'Rating'})
        result = {}
        for i in range(0, len(columns)):
            v = columns[i]
            v['start'] = lines[0].find(v['text'])
            if i > 0:
                c = columns[i - 1]
                c['end'] = v['start']
                c['value'] = lines[1][c['start']:c['end']].strip(" ")
                result[c['name']] = c['value']
        if handle in result['handle']:
            return result
        else:
            return None


def download_apk(handle, tmp_dir, apk_name, apk_tmp):
    """
    Download the APK from Google Play for the given handle.
    :param handle: application handle to download
    :param tmp_dir: download destination directory
    :param apk_name: name of the APK in Minio storage
    :param apk_tmp: apk temporary name
    :return: True if succeed, False otherwise
    """
    device_code_names = ['', '-dc hammerhead', '-dc manta', '-dc cloudbook', '-dc bullhead']
    retry = 5
    exit_code = 1
    # Fix#12 - We have to remove the cached token :S
    shutil.rmtree(os.path.join(str(Path.home()), '.cache/gplaycli/'), ignore_errors = True)
    while retry != 0:
        # Rotate devices
        cmd = 'gplaycli -v -a -t -y -pd %s %s -f %s/' % (
            handle, device_code_names[retry % len(device_code_names)], tmp_dir)
        print(cmd)
        process = sp.Popen(cmd, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
        output = process.communicate()[0]
        print(output)
        exit_code = ('Error' in str(output))
        if exit_code == 0:
            break
        retry -= 1
        time.sleep(2)

    # Upload APK in storage
    apk = Path(apk_tmp)
    if exit_code == 0 and apk.is_file():
        minio_client = Minio(settings.MINIO_URL,
                             access_key = settings.MINIO_ACCESS_KEY,
                             secret_key = settings.MINIO_SECRET_KEY,
                             secure = settings.MINIO_SECURE)
        try:
            minio_client.make_bucket(settings.MINIO_BUCKET, location = "")
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            print(err)
        try:
            minio_client.fput_object(settings.MINIO_BUCKET, apk_name, apk_tmp)
        except ResponseError as err:
            print(err)
            return False

    return exit_code == 0


def clear_analysis_files(tmp_dir, bucket, remove_from_storage = False):
    """
    Clear the analysis files (local + on Minio storage).
    :param tmp_dir: local temporary dir to remove
    :param bucket: Minio object prefix to remove
    :param remove_from_storage: remove objects in Minio if set to True
    """
    print('Removing %s' % tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors = True)
    if remove_from_storage:
        minio_client = Minio(settings.MINIO_URL,
                             access_key = settings.MINIO_ACCESS_KEY,
                             secret_key = settings.MINIO_SECRET_KEY,
                             secure = settings.MINIO_SECURE)
        try:
            try:
                objects = minio_client.list_objects(settings.MINIO_BUCKET, prefix = bucket, recursive = True)
                for obj in objects:
                    minio_client.remove_object(settings.MINIO_BUCKET, obj.object_name)
            except ResponseError as err:
                print(err)
        except ResponseError as err:
            print(err)
