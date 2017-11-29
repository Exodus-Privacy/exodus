from rest_framework import serializers
from reports.models import *


class ReportInfosSerializer(serializers.Serializer):
    creation_date = serializers.DateTimeField()
    report_id = serializers.IntegerField(read_only=True)
    handle = serializers.CharField(max_length=500)
    apk_dl_link = serializers.CharField(max_length=500)
    pcap_upload_link = serializers.CharField(max_length=500)
    flow_upload_link = serializers.CharField(max_length=500)


class LightReportSerializer(serializers.Serializer):
    creation_date = serializers.DateTimeField()
    report_id = serializers.IntegerField(read_only=True)
    web_report_url = serializers.CharField(max_length=500)
    api_report_url = serializers.CharField(max_length=500)
    application_handle = serializers.CharField(max_length=500)
    application_version = serializers.CharField(max_length=500)
    application_version_code = serializers.CharField(max_length=500)
    trackers_count = serializers.IntegerField()
    permission_count = serializers.IntegerField()


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['creation_date', 'found_trackers', 'application']
        depth = 1
