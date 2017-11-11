from rest_framework import serializers


class ReportInfosSerializer(serializers.Serializer):
    creation_date = serializers.DateTimeField()
    report_id = serializers.IntegerField(read_only=True)
    handle = serializers.CharField(max_length=500)
    apk_dl_link = serializers.CharField(max_length=500)
    pcap_upload_link = serializers.CharField(max_length=500)
    flow_upload_link = serializers.CharField(max_length=500)
    