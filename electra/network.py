from utils import *
import time

class TCPDumpConfig:
    def __init__(self, tcpdump_duration, pcap_output, iface, tcpdump_filter):
        self.tcpdump_duration = tcpdump_duration
        self.pcap_output = pcap_output
        self.iface = iface
        self.tcpdump_filter = tcpdump_filter

class TCPDump:
    def __init__(self, config):
        self.config = config

    def start(self):
        cmd = "/usr/bin/sudo /usr/sbin/tcpdump -G %s -W 1 -w %s -i %s %s" % (self.config.tcpdump_duration, self.config.pcap_output, self.config.iface, self.config.tcpdump_filter)
        self.p_tcpdump = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
        time.sleep(5)

    def join(self):
        self.p_tcpdump.communicate()[0]
