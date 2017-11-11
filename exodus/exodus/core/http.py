import pyshark
import tempfile
from reports.models import *
from django.conf import settings
from minio import Minio
from minio.error import (ResponseError)

from .celery import app


@app.task(bind=True)
def analyze_http(self, report_id):
    report = Report.objects.get(pk=report_id)
    net_analysis = NetworkAnalysis.objects.get(report=report)

    # Remove previous HTTP analysis
    try:
        HTTPAnalysis.objects.filter(network_analysis=net_analysis).delete()
    except HTTPAnalysis.DoesNotExist:
        pass

    http_analysis = HTTPAnalysis(network_analysis=net_analysis)
    http_analysis.save()

    # Download pcap file
    minio_client = Minio(settings.MINIO_URL,
                 access_key=settings.MINIO_ACCESS_KEY,
                 secret_key=settings.MINIO_SECRET_KEY,
                 secure=settings.MINIO_SECURE)
    try:
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            minio_client.fget_object(settings.MINIO_BUCKET, report.pcap_file, fp.name)
            cap = pyshark.FileCapture(fp.name)
            for pkt in cap:
                try:
                    if pkt.http.request_method == "POST":
                        payload=HTTPPayload(http_analysis=http_analysis)
                        if pkt.highest_layer != 'HTTP':
                            payload.destination_uri = pkt.http.request_full_uri
                            payload.layer = 'HTTP'
                            payload.payload = pkt.http.__str__() + '\n' + pkt[pkt.highest_layer].__str__()
                            payload.save()
                        else:
                            payload.destination_uri = pkt.http.request_full_uri
                            payload.layer = pkt.highest_layer
                            payload.payload = pkt.http.__str__()
                            payload.save()
                except AttributeError:
                    pass
    except ResponseError as err:
        print(err)