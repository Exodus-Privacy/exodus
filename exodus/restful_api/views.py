# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes

from reports.models import Report
from restful_api.models import ReportInfos
from restful_api.serializers import ReportInfosSerializer
import tempfile
import mimetypes, os, io
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.conf import settings
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists)

from exodus.core.dns import *
from exodus.core.http import *


def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """
    Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
    input stream.

    The stream implements Python 3's newer I/O API (available in Python 2's io module).
    For efficiency, the stream is buffered.
    """
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None
        def readable(self):
            return True
        def readinto(self, b):
            try:
                l = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:l], chunk[l:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0    # indicate EOF
    return io.BufferedReader(IterStream(), buffer_size=buffer_size)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_report_infos(request, r_id):
    if request.method == 'GET':
        report = Report.objects.get(pk=r_id)
        infos = ReportInfos()
        infos.creation_date = report.creation_date
        infos.report_id = report.id
        infos.handle = report.application.handle
        infos.apk_dl_link = '/api/apk/%s/' % report.id
        infos.pcap_upload_link = '/api/pcap/%s/' % report.id
        infos.flow_upload_link = '/api/flow/%s/' % report.id
        serializer = ReportInfosSerializer(infos, many=False)
        return JsonResponse(serializer.data, safe=True)
        
@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_apk(request, r_id):
    if request.method == 'GET':
        report = Report.objects.get(pk=r_id)
        apk_path = report.apk_file

        minioClient = Minio(settings.MINIO_URL,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE)
        try:
            data = minioClient.get_object(settings.MINIO_BUCKET, apk_path)
            return HttpResponse(data.data, content_type=data.getheader('Content-Type'))
        except Exception as err:
            print(err)
            return HttpResponse(status=500)

@csrf_exempt
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def upload_pcap(request, r_id):
    try:
        up_file = request.FILES['file']
        report = Report.objects.get(pk=r_id)
        pcap_name = '%s_%s.pcap' % (report.bucket, report.application.handle)
        minio_client = Minio(settings.MINIO_URL,
                     access_key=settings.MINIO_ACCESS_KEY,
                     secret_key=settings.MINIO_SECRET_KEY,
                     secure=settings.MINIO_SECURE)
        try:
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                for chunk in up_file.chunks():
                    fp.write(chunk)
                print(minio_client.fput_object(settings.MINIO_BUCKET, pcap_name, fp.name))
                fp.close()
        except ResponseError as err:
            print(err)
            return HttpResponse(status=500)
        report.pcap_file = pcap_name
        report.save()
        analyze_dns.delay(r_id)
        analyze_http.delay(r_id)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    return HttpResponse(status=200)

@csrf_exempt
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def upload_flow(request, r_id):
    try:
        up_file = request.FILES['file']
        report = Report.objects.get(pk=r_id)
        flow_name = '%s_%s.flow' % (report.bucket, report.application.handle)
        minio_client = Minio(settings.MINIO_URL,
                     access_key=settings.MINIO_ACCESS_KEY,
                     secret_key=settings.MINIO_SECRET_KEY,
                     secure=settings.MINIO_SECURE)
        try:
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                for chunk in up_file.chunks():
                    fp.write(chunk)
                print(minio_client.fput_object(settings.MINIO_BUCKET, flow_name, fp.name))
                fp.close()
        except ResponseError as err:
            print(err)
            return HttpResponse(status=500)
        report.flow_file = flow_name
        report.save()
        #TODO do analysis
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    return HttpResponse(status=200)