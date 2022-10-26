# coding=utf-8
from __future__ import absolute_import
from .common_dev import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exodus',
        'USER': 'exodus',
        'PASSWORD': os.environ.get('EXODUS_DB_PASSWORD', 'exodus'),
        'HOST': 'db',
        'PORT': 5432,
    }
}

STATIC_ROOT = f'{BASE_DIR}/staticfiles/'
CELERY_BROKER_URL = 'amqp://guest@amqp//'
BROKER_URL = CELERY_BROKER_URL
MINIO_STORAGE_ENDPOINT = 'minio:9000'
