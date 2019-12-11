# coding=utf-8
from __future__ import absolute_import
from .base import *
import os

SECRET_KEY = '9b80473f1b0c7d9f1859cfa754e40e26'

DEBUG = True
ALLOWED_HOSTS = [u'localhost', u'127.0.0.1']

if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'travisci',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
else:
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

STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, '..', 'static'), )

CELERY_BROKER_URL = 'amqp://guest@localhost//'
BROKER_URL = CELERY_BROKER_URL
MINIO_STORAGE_ENDPOINT = '127.0.0.1:9000'
MINIO_STORAGE_ACCESS_KEY = 'exodusexodus'
MINIO_STORAGE_SECRET_KEY = 'exodusexodus'

ALLOW_APK_UPLOAD = True

TRACKERS_AUTO_UPDATE = True
