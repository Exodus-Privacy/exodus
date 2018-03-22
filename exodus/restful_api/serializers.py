from rest_framework import serializers
from reports.models import *
from .models import SearchQuery

class ReportInfosSerializer(serializers.Serializer):
    creation_date = serializers.DateTimeField()
    report_id = serializers.IntegerField(read_only=True)
    handle = serializers.CharField(max_length=500)
    apk_dl_link = serializers.CharField(max_length=500)
    pcap_upload_link = serializers.CharField(max_length=500)
    flow_upload_link = serializers.CharField(max_length=500)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['creation_date', 'found_trackers', 'application']
        depth = 1


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        exclude = ('icon_path', 'report', 'version', 'version_code')


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracker
        fields = '__all__'


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `SearchQuery` instance, given the validated data.
        """
        return SearchQuery(**validated_data)