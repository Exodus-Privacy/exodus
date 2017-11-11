from __future__ import absolute_import
from .base import *

DEBUG = False
ALLOWED_HOSTS = [u'localhost', u'127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exodus_backend',
        'USER': 'exodus_backend',
        'PASSWORD': 'bigpassword',
        'HOST': '192.168.1.119',
        'PORT': '5432',
    }
}
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "storage"),
]

CELERY_BROKER_URL = 'pyamqp://exodus_backend:exodus_backend@192.168.1.119//'
BROKER_URL = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['pickle']
MINIO_URL = '192.168.1.119:9199'
MINIO_ACCESS_KEY = 'totototototo'
MINIO_SECRET_KEY = 'totototototototo'
MINIO_SECURE = False
MINIO_BUCKET = 'exodus_backend'