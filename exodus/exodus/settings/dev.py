# coding=utf-8
from __future__ import absolute_import
from .common_dev import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exodus',
        'USER': 'exodus',
        'PASSWORD': 'exodus',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

CELERY_BROKER_URL = 'amqp://guest@localhost//'
BROKER_URL = CELERY_BROKER_URL
MINIO_STORAGE_ENDPOINT = '127.0.0.1:9000'
