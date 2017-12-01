# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import shutil
import subprocess as sp
from pathlib import Path
from xml.dom import minidom

import yaml
from django.conf import settings
from minio import Minio
from minio.error import (ResponseError)
from trackers.models import Tracker


def grep(file, pattern):
    cmd = '/bin/grep -E "%s" %s' % (pattern, file)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    print(exitCode)
    return exitCode == 0


def download_and_put(url, destination_name):
    import urllib.request, tempfile
    try:
        f = urllib.request.urlopen(url)
        print("Downloading " + url)
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            fp.write(f.read())
            # Upload icon in storage
            minio_client = Minio(settings.MINIO_URL,
                                 access_key=settings.MINIO_ACCESS_KEY,
                                 secret_key=settings.MINIO_SECRET_KEY,
                                 secure=settings.MINIO_SECURE)
            try:
                minio_client.fput_object(settings.MINIO_BUCKET, destination_name, fp.name)
            except ResponseError as err:
                print(err)
            return destination_name
    except Exception as e:
        print(e)
        return ''


def getIcon(icon_name, handle, url=None):
    from bs4 import BeautifulSoup
    import urllib.request, tempfile

    if url is None:
        try:
            address = 'https://play.google.com/store/apps/details?id=%s' % handle
            text = urllib.request.urlopen(address).read()
            soup = BeautifulSoup(text, 'html.parser')
            i = soup.find_all('img', {'class': 'cover-image', 'alt': 'Cover art'})
            if len(i) > 0:
                url = '%s'%i[0]['src']
                if not url.startswith('http'):
                    url = 'https:%s' % url
            else:
                return ''
        except Exception:
            return ''

    return download_and_put(url, icon_name)


def findTrackers(class_list_file):
    trackers = Tracker.objects.order_by('name')
    found = []
    for t in trackers:
        if len(t.code_signature) > 3:
            if grep(class_list_file, t.code_signature):
                found.append(t)
    return found


def getVersionCode(decoded_dir):
    yml = os.path.join(decoded_dir, 'apktool.yml')
    yml_new = os.path.join(decoded_dir, 'apktool.yml.new')
    cmd = '/bin/cat %s | /bin/grep -v "\!\!" > %s' % (yml, yml_new)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode != 0:
        return ''
    with open(yml_new) as f:
        dataMap = yaml.safe_load(f)
        return dataMap['versionInfo']['versionCode']


def getVersion(decoded_dir):
    yml = os.path.join(decoded_dir, 'apktool.yml')
    yml_new = os.path.join(decoded_dir, 'apktool.yml.new')
    cmd = '/bin/cat %s | /bin/grep -v "\!\!" > %s' % (yml, yml_new)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode != 0:
        return ''    
    with open(yml_new) as f:
        dataMap = yaml.safe_load(f)
        return dataMap['versionInfo']['versionName']


def getHandle(decoded_dir):
    xmldoc = minidom.parse(os.path.join(decoded_dir, 'AndroidManifest.xml'))
    man = xmldoc.getElementsByTagName('manifest')[0]
    return man.getAttribute('package')


def getPermissions(decoded_dir):
    xmldoc = minidom.parse(os.path.join(decoded_dir, 'AndroidManifest.xml'))
    permissions = xmldoc.getElementsByTagName('uses-permission')
    perms = []
    for perm in permissions:
        perms.append(perm.getAttribute('android:name'))
    return perms


def getSha256Sum(apk_path):
    cmd = '/usr/bin/sha256sum %s | head -c 64' % apk_path
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    return process.stdout.read()


def decodeAPK(apk_path, decoded_dir):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    apktool = os.path.join(root_dir, "apktool.jar")
    cmd = '/usr/bin/java -jar %s d %s -s -o %s/' % (apktool, apk_path, decoded_dir)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    return exitCode == 0


def listClasses(decoded_dir, class_list_file):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    dexdump = os.path.join(root_dir, "dexdump")
    list_file = '%s/class_list.txt' % decoded_dir
    cmd = '%s %s/classes*.dex > %s; head %s' % (dexdump, decoded_dir, list_file, list_file)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode == 0:
        # Upload class list file
        minio_client = Minio(settings.MINIO_URL,
                             access_key=settings.MINIO_ACCESS_KEY,
                             secret_key=settings.MINIO_SECRET_KEY,
                             secure=settings.MINIO_SECURE)
        try:
            minio_client.fput_object(settings.MINIO_BUCKET, class_list_file, list_file)
        except ResponseError as err:
            print(err)
            return ''
        return list_file
    return ''


def getApplicationInfos(handle):
    # Fix#12 - We have to remove the cached token :S
    shutil.rmtree(os.path.join(str(Path.home()), '.cache/gplaycli/'), ignore_errors=True)
    cmd = 'gplaycli -t -s %s -n 1' % handle
    lines = []
    with sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True) as p:
        for line in iter(p.stdout):
            if 'Traceback' in line or 'Error' in line:
                return None
            lines.append(line.replace('\n', ''))
        if len(lines) != 2:
            return None
        columns = []
        columns.append({'start':0, 'end':0, 'value':'', 'name':'title', 'text':'Title'})
        columns.append({'start':0, 'end':0, 'value':'', 'name':'creator', 'text':'Creator'})
        columns.append({'start':0, 'end':0, 'value':'', 'name':'size', 'text':'Size'})
        columns.append({'start':0, 'end':0, 'value':'', 'name':'downloads', 'text':'Downloads'})
        columns.append({'start':0, 'end':0, 'value':'', 'name':'update', 'text':'Last Update'})
        columns.append({'start':0, 'end':0, 'value':'', 'name':'handle', 'text':'AppID'})
        columns.append({'start':0, 'end':0, 'value':'', 'name':'version', 'text':'Version'})
        columns.append({'start':0, 'end':0, 'value':'', 'name':'rating', 'text':'Rating'})
        result = {}
        for i in range(0,len(columns)):
            v = columns[i]
            v['start'] = lines[0].find(v['text'])
            if i > 0:
                c = columns[i-1]
                c['end'] = v['start']
                c['value'] = lines[1][c['start']:c['end']].strip(" ")
                result[c['name']] = c['value']
        if handle in result['handle']:
            return result
        else:
            return None
