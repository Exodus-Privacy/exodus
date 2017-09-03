import contextlib
import math
import mmap
import os, sys
import re
import subprocess as sp

trackers = [{'name':'Teemo', 'patterns':['databerries']},
            {'name':'FidZup', 'patterns':['fidzup']},
            {'name':'Krux', 'patterns':['krxd\.net']},
            {'name':'Ad4Screen', 'patterns':['ad4screen', 'a4\.tl', 'app4free']},
            {'name':'DoubleClick', 'patterns':['mng-ads\.com', 'doubleclick\.net']},
            {'name':'Weborama', 'patterns':['weborama\.net']},
            {'name':'SmartAd', 'patterns':['smartadserver\.com','saspreview\.com']},
            {'name':'JWPLTx', 'patterns':['jwpltx\.com']},
            {'name':'Loggly', 'patterns':['loggly\.com']},
            {'name':'Xiti', 'patterns':['xiti\.com']},
            {'name':'OutBrain', 'patterns':['outbrain\.com']},
            {'name':'AppsFlyer', 'patterns':['appsflyer\.com']},
            {'name':'Ligatus', 'patterns':['ligatus\.com']},
            {'name':'Widespace', 'patterns':['widespace\.com']},
            {'name':'AppNexus', 'patterns':['adnxs\.com']},
            ] 


def find_all(folder):
    found = []
    for t in trackers:
        # print(t['name'])
        for p in t['patterns']:
            if grep(folder, p):
                found.append(t['name'])
                break
    return found

def grep(folder, pattern):
    cmd = '/bin/grep -r "%s" %s/' % (pattern, folder)
    process = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    # streamdata = process.communicate()[0]
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
