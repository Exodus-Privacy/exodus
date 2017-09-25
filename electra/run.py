import sys, os
import json, time
import subprocess as sp
import requests
from exodus import Exodus
from vbox import VBoxConfig, VBox
from adb import ADB
from network import TCPDumpConfig, TCPDump
from utils import *

# Credentials
username = 'lambda'
password = 'xxxxxxxx'

# Programs
adb_bin = "/home/lambda/Android/Sdk/platform-tools/adb"
adb = ADB(adb_bin)

# Virtual Box
vboxmanage = "/usr/bin/vboxmanage"
vm_name = "Android"
vm_ip = "192.168.1.110"
vm_snapshot = "Android-gmail-account3"
vbox_config = VBoxConfig(vm_name, vm_snapshot, vm_ip, vboxmanage)

# Directories
electra_dir = os.path.dirname(os.path.realpath(__file__))
apk_folder = os.path.join(electra_dir, "apks")
net_folder = os.path.join(electra_dir, "net")

os_run('mkdir -p %s' % apk_folder)
os_run('mkdir -p %s' % net_folder)

DEBUG = True

# Clear all
if not DEBUG:
    os.system("rm -rf %s/*" % apk_folder)
    os.system("rm -rf %s/*" % net_folder)

report_url = sys.argv[1]

exodus = Exodus('http://127.0.0.1:8000', report_url)
exodus.login(username, password)
handle = exodus.get_report_infos()['handle']
print("Downloading the APK")
apk_path = exodus.download_apk(apk_folder)

# Tcpdump
tcpdump_duration = 80
iface = "wlp4s0"
dns_ip = "192.168.1.108"
tcpdump_filter = "\"dst host 192.168.1.110 or src host 192.168.1.110\""
pcap_output = '%s/%s.pcap' % (net_folder, handle)
tcpdump_config = TCPDumpConfig(tcpdump_duration, pcap_output, iface, tcpdump_filter)

vbox = VBox(vbox_config)
if not DEBUG:
    print("Starting VirtualBox VM")
    if not vbox.stop():
        pass
    if not vbox.restore():
        raise SystemError('Unable to restore snapshot')
    if not vbox.start():
        raise SystemError('Unable to start VM')
    time.sleep(10)

    print("Connection ADB to Android")
    if not adb.connect(vbox_config.ip): #TODO adb connect does not use exit code - cunt!!
        pass
    time.sleep(5)
    if not adb.connect(vbox_config.ip):
        pass

    print("Installing the APK")
    if not adb.install(apk_path):
        raise SystemError('Unable to install the APK')
    if not adb.grant(handle, 'android.permission.ACCESS_COARSE_LOCATION'):
        pass

    print("Starting tcpdump")
    tcpdump = TCPDump(tcpdump_config)
    tcpdump.start()

    print("Starting the application")
    if not adb.run(handle):
        raise SystemError('Unable to start the APK')
    if not adb.disconnect(vbox_config.ip):
        pass

    time.sleep(tcpdump_duration)

    print("Stopping VirtualBox VM")
    if not vbox.stop():
        pass

    tcpdump.join()
print("PCAP file saved")

exodus.upload_pcap(pcap_output)

sys.exit(0)
