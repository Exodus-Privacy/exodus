# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated

from exodus.core.dns import *
from exodus.core.http import *
from restful_api.models import *
from restful_api.serializers import *


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_report_infos(request, r_id):
    if request.method == 'GET':
        report = Report.objects.get(pk = r_id)
        infos = ReportInfos()
        infos.creation_date = report.creation_date
        infos.report_id = report.id
        infos.handle = report.application.handle
        infos.apk_dl_link = '/api/apk/%s/' % report.id
        infos.pcap_upload_link = '/api/pcap/%s/' % report.id
        infos.flow_upload_link = '/api/flow/%s/' % report.id
        serializer = ReportInfosSerializer(infos, many = False)
        return JsonResponse(serializer.data, safe = True)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_apk(request, r_id):
    if request.method == 'GET':
        report = Report.objects.get(pk = r_id)
        apk_path = report.apk_file

        minioClient = Minio(settings.MINIO_URL,
                            access_key = settings.MINIO_ACCESS_KEY,
                            secret_key = settings.MINIO_SECRET_KEY,
                            secure = settings.MINIO_SECURE)
        try:
            data = minioClient.get_object(settings.MINIO_BUCKET, apk_path)
            return HttpResponse(data.data, content_type = data.getheader('Content-Type'))
        except Exception as err:
            print(err)
            return HttpResponse(status = 500)


@csrf_exempt
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def upload_pcap(request, r_id):
    try:
        up_file = request.FILES['file']
        report = Report.objects.get(pk = r_id)
        pcap_name = '%s_%s.pcap' % (report.bucket, report.application.handle)
        minio_client = Minio(settings.MINIO_URL,
                             access_key = settings.MINIO_ACCESS_KEY,
                             secret_key = settings.MINIO_SECRET_KEY,
                             secure = settings.MINIO_SECURE)
        try:
            with tempfile.NamedTemporaryFile(delete = True) as fp:
                for chunk in up_file.chunks():
                    fp.write(chunk)
                print(minio_client.fput_object(settings.MINIO_BUCKET, pcap_name, fp.name))
                fp.close()
        except ResponseError as err:
            print(err)
            return HttpResponse(status = 500)
        report.pcap_file = pcap_name
        report.save()
        analyze_dns.delay(r_id)
        analyze_http.delay(r_id)
    except Exception as e:
        print(e)
        return HttpResponse(status = 500)
    return HttpResponse(status = 200)


@csrf_exempt
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def upload_flow(request, r_id):
    try:
        up_file = request.FILES['file']
        report = Report.objects.get(pk = r_id)
        flow_name = '%s_%s.flow' % (report.bucket, report.application.handle)
        minio_client = Minio(settings.MINIO_URL,
                             access_key = settings.MINIO_ACCESS_KEY,
                             secret_key = settings.MINIO_SECRET_KEY,
                             secure = settings.MINIO_SECURE)
        try:
            with tempfile.NamedTemporaryFile(delete = True) as fp:
                for chunk in up_file.chunks():
                    fp.write(chunk)
                print(minio_client.fput_object(settings.MINIO_BUCKET, flow_name, fp.name))
                fp.close()
        except ResponseError as err:
            print(err)
            return HttpResponse(status = 500)
        report.flow_file = flow_name
        report.save()
        # TODO do analysis
    except Exception as e:
        print(e)
        return HttpResponse(status = 500)
    return HttpResponse(status = 200)


def create_reports_list(report_list):
    applications = {}
    for report in report_list:
        if report.application.handle not in applications:
            applications[report.application.handle] = {}
        application = applications[report.application.handle]
        application['name'] = report.application.name
        application['creator'] = report.application.creator
        if 'reports' not in application:
            application['reports'] = []

        application['reports'].append({
            'id': report.id,
            'creation_date': report.creation_date,
            'updated_at': report.updated_at,
            'version': report.application.version,
            'version_code': report.application.version_code,
            'downloads': report.application.downloads,
            'trackers': [t.id for t in report.found_trackers.all()],
        })
    return applications


def create_tracker_list():
    trackers = {}
    for t in Tracker.objects.order_by('id'):
        tracker = {}
        tracker['id'] = t.id
        tracker['name'] = t.name
        tracker['description'] = t.description
        tracker['creation_date'] = t.creation_date
        tracker['code_signature'] = t.code_signature
        tracker['network_signature'] = t.network_signature
        tracker['website'] = t.website
        trackers[t.id] = tracker
    return trackers


@csrf_exempt
@api_view(['GET'])
@authentication_classes(())
@permission_classes(())
def get_all_reports(request):
    if request.method == 'GET':
        report_list = Report.objects.order_by('-creation_date')[:500]
        applications = create_reports_list(report_list)
        trackers = create_tracker_list()
        return JsonResponse({'applications': applications, 'trackers': trackers})


@csrf_exempt
@api_view(['GET'])
@authentication_classes(())
@permission_classes(())
def get_all_trackers(request):
    if request.method == 'GET':
        trackers = create_tracker_list()
        return JsonResponse({'trackers': trackers})


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_all_applications(request):
    if request.method == 'GET':
        try:
            applications = Application.objects.order_by('name', 'handle').distinct('name', 'handle')
            serializer = ApplicationSerializer(applications, many = True)
            return JsonResponse({'applications': serializer.data}, safe = False)
        except Application.DoesNotExist:
            return JsonResponse({}, safe = True)


@csrf_exempt
@api_view(['GET'])
@authentication_classes(())
@permission_classes(())
def search_strict_handle(request, handle):
    if request.method == 'GET':
        try:
            reports = Report.objects.filter(application__handle = handle)
        except Report.DoesNotExist:
            return JsonResponse({}, safe = True)
        return JsonResponse(create_reports_list(reports))


@csrf_exempt
@api_view(['GET'])
@authentication_classes(())
@permission_classes(())
def get_report_details(request, r_id):
    if request.method == 'GET':
        try:
            report = Report.objects.get(pk = r_id)
        except Report.DoesNotExist:
            raise Http404('No reports found')
        serializer = ReportSerializer(report, many = False)
        return JsonResponse(serializer.data, safe = True)


@csrf_exempt
@api_view(['POST'])
@authentication_classes(())
@permission_classes(())
def search(request):
    data = JSONParser().parse(request)
    serializer = SearchQuerySerializer(data = data)
    if serializer.is_valid():
        query = serializer.create(serializer.validated_data)
        limit = max(2, query.limit)
        if len(query.query) >= 3:
            if query.type == 'application':
                try:
                    applications = Application.objects.filter(
                        Q(handle__icontains = query.query) | Q(name__icontains = query.query)).order_by('name', 'handle').distinct('name', 'handle')[:limit]
                except Application.DoesNotExist:
                    return JsonResponse([], safe = False)
                serializer = ApplicationSerializer(applications, many = True)
                return JsonResponse({'results': serializer.data}, safe = False)
            elif query.type == 'tracker':
                try:
                    applications = Tracker.objects.filter(
                        Q(name__icontains = query.query) | Q(description__icontains = query.query)).order_by('name')[:limit]
                except Tracker.DoesNotExist:
                    return JsonResponse([], safe = False)
                serializer = TrackerSerializer(applications, many = True)
                return JsonResponse({'results': serializer.data}, safe = False)
    return JsonResponse([], safe = False)
