# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-24 16:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReportInfos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField()),
                ('report_id', models.IntegerField()),
                ('handle', models.CharField(max_length=500)),
                ('apk_dl_link', models.CharField(max_length=500)),
                ('pcap_upload_link', models.CharField(max_length=500)),
                ('flow_upload_link', models.CharField(max_length=500)),
            ],
        ),
    ]
