from rest_framework import serializers
from reports.models import Report, Application
from trackers.models import Tracker, TrackerCategory
from .models import SearchQuery


class CertificateSerializer(serializers.Serializer):
    has_expired = serializers.BooleanField()
    serial_number = serializers.CharField()
    issuer = serializers.CharField()
    subject = serializers.CharField()
    fingerprint = serializers.CharField()


class ReportInfosSerializer(serializers.Serializer):
    creation_date = serializers.DateTimeField()
    report_id = serializers.IntegerField(read_only=True)
    handle = serializers.CharField(max_length=500)
    apk_dl_link = serializers.CharField(max_length=500)
    certificate = CertificateSerializer(required=False)


class TrackerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerCategory
        fields = ('name', )


class TrackerSerializerWithCategories(serializers.ModelSerializer):
    category = TrackerCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Tracker
        exclude = []


class ReportSerializer(serializers.ModelSerializer):
    found_trackers = TrackerSerializerWithCategories(many=True, read_only=True)

    class Meta:
        model = Report
        fields = ['creation_date', 'found_trackers', 'application']
        depth = 1


class ApplicationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'handle', 'app_uid', 'source']


class ApplicationSerializer(serializers.ModelSerializer):
    class TimestampField(serializers.Field):
        def to_representation(self, value):
            return value.timestamp()

    report_updated_at = TimestampField(source='report.updated_at')

    class Meta:
        model = Application
        fields = ['id', 'handle', 'name', 'creator', 'downloads', 'app_uid',
                  'source', 'icon_phash', 'report_updated_at']


class SearchApplicationSerializer(serializers.ModelSerializer):
    class TimestampField(serializers.Field):
        def to_representation(self, value):
            return value.timestamp()

    report_updated_at = TimestampField(source='report.updated_at')

    class Meta:
        model = Application
        fields = ['id', 'handle', 'name', 'creator', 'downloads', 'app_uid',
                  'icon_phash', 'report_updated_at', 'permissions_count',
                  'trackers_count', 'permissions_class', 'trackers_class',
                  'version']


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracker
        exclude = ['apps_number', 'apps_percent']


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `SearchQuery` instance, given the validated data.
        """
        return SearchQuery(**validated_data)
