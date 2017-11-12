from __future__ import absolute_import
from .base import *

DEBUG = False
ALLOWED_HOSTS = [u'localhost', u'127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exodus',
        'USER': 'exodus',
        'PASSWORD': '82b0a4e31030851dd88fba45715bbf558ba73e44140439c0f42113904806bdea',
        'HOST': '{{pg_host}}',
        'PORT': '{{pg_port}}',
    }
}

STATIC_ROOT = '/home/lambda/Make/Exodus/exodus/static'
MEDIA_ROOT = '/home/lambda/Make/Exodus/exodus/storage'
STATIC_URL = '/static/'
MEDIA_URL = '/storage/'
CELERY_BROKER_URL = 'pyamqp://{{rabbitmq_user}}:{{rabbitmq_password}}@{{rabbitmq_host}}//'