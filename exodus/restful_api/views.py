# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes

from reports.models import *
from restful_api.models import *
from restful_api.serializers import *
import tempfile
from django.conf import settings
from minio import Minio
from minio.error import (ResponseError)

from exodus.core.dns import *
from exodus.core.http import *


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


@csrf_exempt
@api_view(['GET'])
def get_all_reports(request):
    if request.method == 'GET':
        report_list = Report.objects.order_by('-creation_date')
        reports = [LightReport(report) for report in report_list]
        serializer = LightReportSerializer(reports, many=True)
        return JsonResponse(serializer.data, safe=True)


@csrf_exempt
@api_view(['GET'])
def get_report_details(request, r_id):
    if request.method == 'GET':
        try:
            report = Report.objects.get(pk=r_id)
        except Report.DoesNotExist:
            raise Http404("No reports found")
        serializer = ReportSerializer(report, many=False)
        return JsonResponse(serializer.data, safe=True)