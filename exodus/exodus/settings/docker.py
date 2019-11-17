# coding=utf-8
from __future__ import absolute_import
from .base import *

SECRET_KEY = '9b80473f1b0c7d9f1859cfa754e40e26'

DEBUG = True
ALLOWED_HOSTS = [u'localhost', u'127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exodus',
        'USER': 'exodus',
        'PASSWORD': 'exodus',
        'HOST': 'db',
        'PORT': 5432,
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, '..', 'static'), )

CELERY_BROKER_URL = 'amqp://guest@amqp//'
BROKER_URL = CELERY_BROKER_URL
MINIO_URL = 'minio:9000'
MINIO_ACCESS_KEY = 'exodusexodus'
MINIO_SECRET_KEY = 'exodusexodus'
MINIO_SECURE = False
MINIO_BUCKET = 'exodus'
