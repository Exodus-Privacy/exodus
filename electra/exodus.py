import requests
import json, os

EXODUS_LOGIN_URI = '/api/get_auth_token/'

class Exodus:
    def __init__(self, host, report_info_uri):
        self.host = host
        self.report_info_uri = report_info_uri
        self.access_token = ''
        self.report_info = None

    def login(self, username, password):
        r = requests.post('%s%s' % (self.host, EXODUS_LOGIN_URI), 
                json={'username':username, 'password':password})
        ret_code = r.status_code
        if ret_code != 200:
            raise ConnectionError('Unable to login')
        self.access_token = r.json()['token']

    def get_report_infos(self):
        r=requests.get('%s%s' % (self.host, self.report_info_uri), 
            headers={"Authorization":"Token %s"%self.access_token})
        ret_code = r.status_code
        if ret_code != 200:
            raise ConnectionError('Unable to get report info')
        self.report_info = r.json()
        print(self.report_info)
        return self.report_info

    def download_apk(self, destination):
        url = '%s%s' % (self.host, self.report_info['apk_dl_link'])
        local_filename = '%s.apk' % self.report_info['handle']
        r = requests.get(url, stream=True, headers={'Authorization':'Token %s'%self.access_token})
        local_path = os.path.join(destination, local_filename)
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
        ret_code = r.status_code
        if ret_code != 200:
            raise ConnectionError('Unable to download the APK')
        return local_path

    def upload_pcap(self, pcap_file):
        url = '%s%s' % (self.host, self.report_info['pcap_upload_link'])
        with open(pcap_file, 'rb') as f: 
            r = requests.post(url, files={'file': f}, 
                headers={"Authorization":"Token %s"%self.access_token, "Content-Disposition":"attachment; filename=%s"%os.path.basename(pcap_file)}
                )
            ret_code = r.status_code
            if ret_code != 200:
                raise ConnectionError('Unable to upload the PCAP file')

    def upload_flow(self, flow_file):
        url = '%s%s' % (self.host, self.report_info['flow_upload_link'])
        with open(flow_file, 'rb') as f: 
            r = requests.post(url, files={'file': f}, 
                headers={"Authorization":"Token %s"%self.access_token, "Content-Disposition":"attachment; filename=%s"%os.path.basename(flow_file)}
                )
            ret_code = r.status_code
            if ret_code != 200:
                raise ConnectionError('Unable to upload the FLOW file')