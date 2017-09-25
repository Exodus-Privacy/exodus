from utils import *

class VBoxConfig:
    def __init__(self, vm, snapshot, ip, vbox_bin):
        self.vm = vm
        self.snapshot = snapshot
        self.ip = ip
        self.vbox_bin = vbox_bin


class VBox:
    def __init__(self, config):
        self.config = config

    def start(self):
        cmd = 'vboxmanage startvm "%s"' % self.config.vm
        return os_run(cmd) == 0

    def stop(self):
        cmd = 'vboxmanage controlvm "%s" poweroff' % self.config.vm
        return os_run(cmd) == 0

    def restore(self):
        cmd = 'vboxmanage snapshot "%s" restore %s' % (self.config.vm, self.config.snapshot)
        return os_run(cmd) == 0