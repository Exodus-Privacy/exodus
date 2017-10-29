from utils import *
import os
import time
import signal
import mitmproxy.tools

class TCPDumpConfig:
    def __init__(self, tcpdump_duration, pcap_output, iface, tcpdump_filter):
        self.tcpdump_duration = tcpdump_duration
        self.pcap_output = pcap_output
        self.iface = iface
        self.tcpdump_filter = tcpdump_filter

class MITMProxyConfig:
    def __init__(self, flow_output, port):
        self.flow_output = flow_output
        self.port = port

class TCPDump:
    def __init__(self, config):
        self.config = config

    def start(self):
        cmd = "/usr/bin/sudo /usr/sbin/tcpdump -G %s -W 1 -w %s -i %s %s" % (self.config.tcpdump_duration, self.config.pcap_output, self.config.iface, self.config.tcpdump_filter)
        self.p_tcpdump = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
        time.sleep(5)

    def join(self):
        self.p_tcpdump.communicate()[0]

class MITMProxy:
    def __init__(self, config):
        self.config = config

    def start(self):
        cmd = "mitmdump -z -T --host -p %s -w %s" % (self.config.port, self.config.flow_output)
        print(cmd)
        self.p_mitmproxy = sp.Popen(cmd, stdout=sp.PIPE, shell=True, preexec_fn=os.setsid)
        time.sleep(5)

    def stop(self):
        self.p_mitmproxy.send_signal(signal.SIGINT)
        os.killpg(os.getpgid(self.p_mitmproxy.pid), signal.SIGINT)
        time.sleep(1)
        self.p_mitmproxy.kill()
