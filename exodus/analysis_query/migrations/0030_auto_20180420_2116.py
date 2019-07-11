# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-12 12:04
from __future__ import unicode_literals

import analysis_query.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis_query', '0029_auto_20170925_1440'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysisrequest',
            name='apk',
        ),
        migrations.RemoveField(
            model_name='analysisrequest',
            name='storage_path',
        ),
        migrations.AddField(
            model_name='analysisrequest',
            name='bucket',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='analysisrequest',
            name='in_error',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='analysisrequest',
            name='report_id',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='analysisrequest',
            name='handle',
            field=models.CharField(max_length=500, validators=[analysis_query.models.validate_handle]),
        ),
        migrations.AlterField(
            model_name='analysisrequest',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]