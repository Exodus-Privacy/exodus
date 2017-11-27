# coding=utf-8
from __future__ import absolute_import
from .base import *

SECRET_KEY = '{{secret_key}}'

DEBUG = False
ALLOWED_HOSTS = [u'{{exodus.frontend.public.ip}}', u'{{exodus.frontend.ip}}', u'{{exodus.domain}}', u'127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{{pg.database}}',
        'USER': '{{pg.user}}',
        'PASSWORD': '{{pg.password}}',
        'HOST': '{{pg.host}}',
        'PORT': '{{pg.port}}',
    }
}
STATIC_URL = '/static/'

CELERY_BROKER_URL = 'pyamqp://{{rabbitmq.user}}:{{rabbitmq.password}}@{{rabbitmq.host}}//'
BROKER_URL = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['pickle']
MINIO_URL = '{{minio.host}}:{{minio.port}}'
MINIO_ACCESS_KEY = '{{minio.access_key}}'
MINIO_SECRET_KEY = '{{minio.secret_key}}'
MINIO_SECURE = {{minio.secure}}
MINIO_BUCKET = 'exodus'