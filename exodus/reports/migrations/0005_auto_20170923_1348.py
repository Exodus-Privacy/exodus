# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-23 13:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20170923_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apk',
            name='application',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='reports.Application'),
        ),
        migrations.AlterField(
            model_name='application',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='reports.Report'),
        ),
    ]
