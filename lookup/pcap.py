import sys, os
import zipfile
import subprocess as sp
import yaml
import datetime
import pyshark
import pprint

pp = pprint.PrettyPrinter(indent=2)
def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

def get_dns(path):
    dns = []
    cap = pyshark.FileCapture(path)
    for pkt in cap:
        try:
            if pkt.dns and pkt.dns.qry_name and pkt.dns.a:
                dns.append({'query':pkt.dns.qry_name, 'host': pkt.dns.a})
        except AttributeError:
            pass
    return dns

def get_http_post(path):
    post = []
    cap = pyshark.FileCapture(path)
    for pkt in cap:
        try:
            if pkt.http.request_method == "POST":
                if pkt.highest_layer  != 'HTTP':
                    post.append({'uri': pkt.http.request_full_uri, 'data': pkt.http.__str__(), pkt.highest_layer:pkt[pkt.highest_layer].__str__()})
                else:
                    post.append({'uri': pkt.http.request_full_uri, 'data': pkt.http.__str__()})
        except AttributeError:
            pass
    return post