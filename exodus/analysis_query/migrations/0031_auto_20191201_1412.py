# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-01 14:12
from __future__ import unicode_literals

import analysis_query.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis_query', '0030_auto_20180420_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisrequest',
            name='apk',
            field=models.FileField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='analysisrequest',
            name='handle',
            field=models.CharField(default='', max_length=500, validators=[analysis_query.models.validate_handle]),
        ),
    ]
