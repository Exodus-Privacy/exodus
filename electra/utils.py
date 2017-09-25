import subprocess as sp

def os_run(cmd):
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    output = process.communicate()[0]
    return process.returncode 