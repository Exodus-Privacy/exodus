from utils import *

class ADB:
    def __init__(self, adb_bin):
        self.adb_bin = adb_bin

    def connect(self, ip):
        cmd = '%s connect %s' % (self.adb_bin, ip)
        return os_run(cmd) == 0

    def install(self, apk):
        cmd = '%s install %s' % (self.adb_bin, apk)
        return os_run(cmd) == 0

    def grant(self, handle, permission):
        cmd = '%s shell pm grant %s %s' % (self.adb_bin, handle, permission)
        return os_run(cmd) == 0

    def run(self, handle):
        cmd = '%s shell monkey -p %s 25' % (self.adb_bin, handle)
        return os_run(cmd) == 0

    def disconnect(self, ip):
        cmd = '%s disconnect %s' % (self.adb_bin, ip)
        return os_run(cmd) == 0