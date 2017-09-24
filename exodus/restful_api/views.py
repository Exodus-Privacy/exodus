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

import mimetypes, os
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper

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
        filename = os.path.basename(apk_path)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(apk_path, 'rb'), chunk_size),
                content_type=mimetypes.guess_type(apk_path)[0])
        response['Content-Length'] = os.path.getsize(apk_path)    
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def upload_pcap(request, r_id):
    try:
        up_file = request.FILES['file']
        print(up_file)
        report = Report.objects.get(pk=r_id)
        storage_path = report.storage_path
        destination_path = os.path.join(storage_path, up_file.name)
        destination = open(destination_path, 'wb+')
        for chunk in up_file.chunks():

            destination.write(chunk)
        destination.close()
        report.pcap_file = destination_path
        report.save()
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    return HttpResponse(status=200)