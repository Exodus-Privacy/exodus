from __future__ import absolute_import
from .base import *

DEBUG = False
ALLOWED_HOSTS = [u'localhost', u'127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exodus_backend',
        'USER': 'exodus_backend',
        'PASSWORD': '82b0a4e31030851dd88fba45715bbf558ba73e44140439c0f42113904806bdea',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/home/lambda/Make/Exodus/exodus_backend/static/'
MEDIA_ROOT = '/home/lambda/Make/Exodus/exodus_backend/storage/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "storage"),
]

CELERY_BROKER_URL = 'pyamqp://guest:guest@localhost//'
BROKER_URL = CELERY_BROKER_URL