# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from minio import Minio
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from reports.models import Application, Report, Certificate
from trackers.models import Tracker
from restful_api.serializers import ApplicationSerializer, TrackerSerializer,\
    ReportInfosSerializer, ReportSerializer, SearchQuerySerializer,\
    SearchApplicationSerializer, ApplicationShortSerializer


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_report_infos(request, r_id):
    if request.method == 'GET':
        try:
            report = Report.objects.get(pk=r_id)
        except Report.DoesNotExist:
            raise Http404('No report found')

        certificate = None
        if hasattr(report.application, 'apk'):
            certificates = Certificate.objects.filter(apk=report.application.apk)
            certificate = certificates.first()

        obj = {
            'creation_date': report.creation_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'report_id': report.id,
            'handle': report.application.handle,
            'certificate': certificate,
            'apk_dl_link': '',
        }
        if request.user.is_staff:
            obj['apk_dl_link'] = '/api/apk/{}/'.format(report.id)

        serializer = ReportInfosSerializer(obj, many=False)
        return JsonResponse(serializer.data, safe=True)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, IsAdminUser))
def get_apk(request, r_id):
    if request.method == 'GET':
        try:
            report = Report.objects.get(pk=r_id)
        except Report.DoesNotExist:
            raise Http404('No report found')

        apk_path = report.apk_file

        minioClient = Minio(
            settings.MINIO_STORAGE_ENDPOINT,
            access_key=settings.MINIO_STORAGE_ACCESS_KEY,
            secret_key=settings.MINIO_STORAGE_SECRET_KEY,
            secure=settings.MINIO_STORAGE_USE_HTTPS
        )
        try:
            data = minioClient.get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, apk_path)
            return HttpResponse(
                data.data, content_type=data.getheader('Content-Type'))
        except Exception as err:
            print(err)
            return HttpResponse(status=500)


def _get_reports_list(report_list):
    reports = {}
    for report in report_list:
        if report.application.handle not in reports:
            reports[report.application.handle] = {}
        app = reports[report.application.handle]
        app['name'] = report.application.name
        app['creator'] = report.application.creator
        if 'reports' not in app:
            app['reports'] = []

        app['reports'].append({
            'id': report.id,
            'creation_date': report.creation_date,
            'updated_at': report.updated_at,
            'version': report.application.version,
            'version_code': report.application.version_code,
            'source': report.application.source,
            'downloads': report.application.downloads,
            'trackers': [t.id for t in report.found_trackers.all()],
        })
    return reports


def _get_tracker_list():
    trackers = {}
    for t in Tracker.objects.order_by('id'):
        tracker = {
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'creation_date': t.creation_date,
            'code_signature': t.code_signature,
            'network_signature': t.network_signature,
            'website': t.website,
            'categories': [c.name for c in t.category.all()]
        }
        trackers[t.id] = tracker
    return trackers


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_all_reports(request):
    if request.method == 'GET':
        report_list = Report.objects.order_by('-creation_date')[:500]
        applications = _get_reports_list(report_list)
        trackers = _get_tracker_list()
        return JsonResponse(
            {
                'applications': applications,
                'trackers': trackers
            }
        )


@csrf_exempt
@api_view(['GET'])
@authentication_classes(())
@permission_classes(())
def get_all_trackers(request):
    if request.method == 'GET':
        trackers = _get_tracker_list()
        return JsonResponse({'trackers': trackers})


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_all_applications(request):
    if request.method == 'GET':
        try:
            applications = Application.objects.order_by('handle', '-source').distinct('handle', 'source')
            if request.GET.get('option', 'full') == 'short':
                serializer = ApplicationShortSerializer(applications, many=True)
            else:
                serializer = ApplicationSerializer(applications, many=True)
            return JsonResponse({'applications': serializer.data}, safe=False)
        except Application.DoesNotExist:
            return JsonResponse({}, safe=True)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def search_strict_handle(request, handle):
    if request.method == 'GET':
        try:
            reports = Report.objects.filter(application__handle=handle).order_by('-creation_date')
        except Report.DoesNotExist:
            return JsonResponse({}, safe=True)
        return JsonResponse(_get_reports_list(reports))


@csrf_exempt
@api_view(['GET'])
@authentication_classes(())
@permission_classes(())
def search_latest_report(request, handle):
    if request.method == 'GET':
        try:
            report = Report.objects.filter(application__handle=handle).order_by('-creation_date').first()
            if not report:
                raise Report.DoesNotExist
        except Report.DoesNotExist:
            return JsonResponse({}, safe=True)
        obj = {
            'id': report.id,
            'name': report.application.name,
            'creation_date': report.creation_date
        }
        return JsonResponse(obj)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_report_details(request, r_id):
    if request.method == 'GET':
        try:
            report = Report.objects.get(pk=r_id)
        except Report.DoesNotExist:
            raise Http404('No reports found')
        serializer = ReportSerializer(report, many=False)
        return JsonResponse(serializer.data, safe=True)


def _get_applications(input, limit):
    exact_handle_matches = Application.objects.filter(Q(handle=input)).order_by('name', 'handle', '-report__creation_date').distinct('name', 'handle')[:limit]
    if exact_handle_matches.count() > 0:
        return exact_handle_matches

    applications = Application.objects.annotate(
        similarity=TrigramSimilarity('name', input),
    ).filter(
        similarity__gt=0.3
    ).order_by(
        '-similarity', 'name', 'handle', '-report__creation_date'
    ).distinct(
        'similarity', 'name', 'handle'
    )[:limit]
    return applications


@csrf_exempt
@api_view(['POST'])
@authentication_classes(())
@permission_classes(())
def search(request):
    data = JSONParser().parse(request)
    serializer = SearchQuerySerializer(data=data)
    if serializer.is_valid():
        query = serializer.create(serializer.validated_data)
        limit = max(2, query.limit)
        if len(query.query) >= 3:
            if query.type == 'application':
                try:
                    applications = _get_applications(query.query, limit)
                except Application.DoesNotExist:
                    return JsonResponse([], safe=False)
                serializer = SearchApplicationSerializer(applications, many=True)
                return JsonResponse({'results': serializer.data}, safe=False)
            elif query.type == 'tracker':
                try:
                    trackers = Tracker.objects.filter(
                        Q(name__icontains=query.query) | Q(description__icontains=query.query)).order_by('name')[:limit]
                except Tracker.DoesNotExist:
                    return JsonResponse([], safe=False)
                serializer = TrackerSerializer(trackers, many=True)
                return JsonResponse({'results': serializer.data}, safe=False)
    return JsonResponse([], safe=False)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def search_strict_handle_details(request, handle):
    if request.method == 'GET':
        try:
            reports = Report.objects.filter(application__handle=handle)
            details = []
            for report in reports:
                app = report.application
                details.append({
                    'handle': app.handle,
                    'app_name': app.name,
                    'uaid': app.app_uid,
                    'version_name': app.version,
                    'version_code': app.version_code,
                    'source': app.source,
                    'icon_hash': app.icon_phash,
                    'apk_hash': app.apk.sum,
                    'created': report.creation_date,
                    'updated': report.updated_at,
                    'report': report.id,
                    'creator': app.creator,
                    'downloads': app.downloads,
                    'trackers': [t.id for t in report.found_trackers.all()],
                    'permissions': [p.name for p in app.permission_set.all()]
                })
        except Report.DoesNotExist:
            return JsonResponse({}, safe=True)
        return JsonResponse(details, safe=False)


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_trackers_count(request):
    if request.method == 'GET':
        return JsonResponse({'count': Tracker.objects.count()})


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_reports_count(request):
    if request.method == 'GET':
        return JsonResponse({'count': Report.objects.count()})


@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_applications_count(request):
    if request.method == 'GET':
        return JsonResponse({'count': Application.objects.distinct('handle').count()})
