from xml.dom import minidom
import sys, os
import zipfile
import subprocess as sp
import yaml
import datetime


root_dir = os.path.dirname(os.path.realpath(__file__))
apktool = os.path.join(root_dir, "apktool.jar")

def get_data(apk, apk_path, decoded_apk_path):
    yml = os.path.join(decoded_apk_path, 'apktool.yml')
    yml_new = os.path.join(decoded_apk_path, 'apktool.yml.new')
    cmd = '/bin/cat %s | /bin/grep -v "\!\!" > %s' % (yml, yml_new)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    exitCode = process.returncode
    if exitCode != 0:
        return[]
    data = {}
    data['report'] = {
        'date' : datetime.datetime.utcnow().isoformat(),
        'apk' : {
            'name': apk,
            'path': apk_path,
            'sha256': sha256sum(apk_path)
        },
    }
    data['application'] = {}
    package = get_package(apk, decoded_apk_path)
    data['application']['link'] = 'https://play.google.com/store/apps/details?id=%s' % package
    data['application']['handle'] = package
    with open(yml_new) as f:
        dataMap = yaml.safe_load(f)
        data['application']['version'] = dataMap['versionInfo']['versionName']
        data['application']['permissions'] = get_permissions(apk, decoded_apk_path)
        return data

def get_package(apk, decoded_apk_path):
    xmldoc = minidom.parse(os.path.join(decoded_apk_path, 'AndroidManifest.xml'))
    man = xmldoc.getElementsByTagName('manifest')[0]
    return man.getAttribute('package')

def get_permissions(apk, decoded_apk_path):
    xmldoc = minidom.parse(os.path.join(decoded_apk_path, 'AndroidManifest.xml'))
    permissions = xmldoc.getElementsByTagName('uses-permission')
    perms = []
    for perm in permissions:
        perms.append(perm.getAttribute('android:name'))
    return perms

def sha256sum(apk_path):
    cmd = '/usr/bin/sha256sum %s | head -c 64' % apk_path
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    sum = process.stdout.read()
    return sum

def decode(apk_path, decoded_apk_path):
    cmd = '/usr/bin/java -jar %s d %s -o %s/' % (apktool, apk_path, decoded_apk_path)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    # while True:
    #     nextline = process.stdout.readline()
    #     if nextline == '' and process.poll() is not None:
    #         break
    #     sys.stdout.write(nextline)
    #     sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode
    # if exitCode == 0:
    #     print(cmd)          
    return exitCode == 0