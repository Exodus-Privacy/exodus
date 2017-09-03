from xml.dom import minidom
import sys, os
import zipfile
from lookup import trackers, app, pcap
import json, time
import subprocess as sp
import requests

# Programs
gplaycli = "/usr/local/bin/gplaycli"
adb = "/home/lambda/Android/Sdk/platform-tools/adb"

# Virtual Box
vboxmanage = "/usr/bin/vboxmanage"
vm_name = "Android"
vm_ip = "192.168.1.110"
vm_snapshot = "Android-setup-geoloc"

# Tcpdump
tcpdump_duration = 60
iface = "wlp4s0"
dns_ip = "192.168.1.108"
tcpdump_filter = "\"dst host 192.168.1.110 or src host 192.168.1.110\""
# tcpdump_filter = "ip.src == 192.168.1.110 ||  ip.src == 192.168.1.108"

# Directories
exodus_dir = os.path.dirname(os.path.realpath(__file__))
apk_folder = os.path.join(exodus_dir, "apks")
extracted_folder = os.path.join(exodus_dir, "extracted")
decoded_folder = os.path.join(exodus_dir, "decoded")
net_folder = os.path.join(exodus_dir, "net")

apk_list_file = sys.argv[1]

def os_run(cmd):
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    return process.returncode 

    
# Clear all
os.system("rm -rf %s/*" % apk_folder)
os.system("rm -rf %s/*" % extracted_folder)
os.system("rm -rf %s/*" % decoded_folder)
os.system("rm -rf %s/*" % net_folder)

# Download APK
os.system("/usr/local/bin/gplaycli -F %s -f %s" % (apk_list_file, apk_folder))

# For each applications
apk_names = [fn for fn in os.listdir(apk_folder)
              if any(fn.endswith(ext) for ext in ["apk"])]
print(apk_names)
for apk_name in apk_names:
    report = {}
    apk_path = os.path.join(apk_folder, apk_name)
    extracted_apk_path = os.path.join(extracted_folder, apk_name)
    decoded_apk_path = os.path.join(decoded_folder, apk_name)

    print("Extracting %s" % apk_name)
    zip_ref = zipfile.ZipFile(apk_path, 'r')
    zip_ref.extractall(extracted_apk_path)
    zip_ref.close()

    print("Decoding %s" % apk_name)
    app.decode(apk_path, decoded_apk_path)

    print("Lookup in %s" % apk_name)
    app_data = app.get_data(apk_name, apk_path, decoded_apk_path)
    app_data['report']['trackers'] = trackers.find_all(extracted_apk_path)

    handle = app_data['application']['handle']
    pcap_output = '%s/%s.pcap' % (net_folder, apk_name)

    print("Starting VirtualBox VM")
    cmd = 'vboxmanage controlvm "%s" poweroff' % vm_name
    if os_run(cmd) != 0:
        print("** Aborting analysis of %s - Unable to stop VM" % apk_name)
    #     break
    time.sleep(5)
    cmd = 'vboxmanage snapshot "%s" restore %s' % (vm_name, vm_snapshot)
    if os_run(cmd) != 0:
        print("** Aborting analysis of %s - Unable to restore snapshot" % apk_name)
        break
    time.sleep(5)
    cmd = 'vboxmanage startvm "%s"' % vm_name
    if os_run(cmd) != 0:
        print("** Aborting analysis of %s - Unable to start VM" % apk_name)
        break
    time.sleep(10)

    print("Connecting ADB to Android")
    cmd = '%s connect %s' % (adb, vm_ip)
    print(cmd)
    if os_run(cmd) != 0:
        break 
    time.sleep(5)
    if os_run(cmd) != 0:
        break 
    time.sleep(5)
    print("Installing %s" % apk_name)
    cmd = '%s install %s' % (adb, apk_path)
    print(cmd)
    if os_run(cmd) != 0:
        print("** Aborting analysis of %s - Unable to install app" % apk_name)  
        break  
    cmd = '%s shell pm grant %s android.permission.ACCESS_COARSE_LOCATION' % (adb, handle)
    print(cmd)
    if os_run(cmd) != 0:
        print("** Ooooops Unable to set permission")  
    
    print("Starting network sniffing")
    cmd = "/usr/bin/sudo /usr/sbin/tcpdump -G %s -W 1 -w %s -i %s %s" % (tcpdump_duration, pcap_output, iface, tcpdump_filter)
    print(cmd)
    p = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
    time.sleep(5)

    print("Starting %s application" % apk_name)
    cmd = '%s shell monkey -p %s 1' % (adb, handle)
    if os_run(cmd) != 0:
        print("** Aborting analysis of %s - Unable to start application" % apk_name)  
        break  
    cmd = '%s disconnect %s' % (adb, vm_ip)
    print(cmd)
    if os_run(cmd) != 0:
        break 

    time.sleep(tcpdump_duration)

    print("Stopping VirtualBox VM")
    cmd = 'vboxmanage controlvm "%s" poweroff' % vm_name
    if os_run(cmd) != 0:
        print("** Aborting analysis of %s - Unable to stop VM" % apk_name)
        break

    print("Analysing network activity of %s" % apk_name)
    app_data['report']['network'] = {}
    app_data['report']['network']['dns'] = pcap.get_dns(pcap_output)
    app_data['report']['network']['http'] = {}
    app_data['report']['network']['http']['post'] = pcap.get_http_post(pcap_output)

    print("Exporting report of %s" % apk_name)
    print json.dumps(app_data, sort_keys=True, indent=4)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post("http://localhost:5000/report", json=json.dumps(app_data), headers=headers)
    print(r)