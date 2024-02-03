# coding=utf-8
from __future__ import absolute_import
from .base import *

default_secret_key = '9b80473f1b0c7d9f1859cfa754e40e26'
SECRET_KEY = env('EXODUS_SECRET_KEY', default=default_secret_key)

ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'
STATIC_ROOT = f'{BASE_DIR}/static/'
STATICFILES_DIRS = [f'{APPS_DIR}/static']

MINIO_STORAGE_ACCESS_KEY = env('EXODUS_MINIO_ROOT_USER', default='exodusexodus')
MINIO_STORAGE_SECRET_KEY = env('EXODUS_MINIO_ROOT_PASSWORD', default='exodusexodus')

ALLOW_APK_UPLOAD = True

TRACKERS_AUTO_UPDATE = True

customization = env('EXODUS_CUSTOMIZATION', default='')
if customization:
    INSTALLED_APPS = [customization] + INSTALLED_APPS

CSRF_COOKIE_SECURE = env.bool('EXODUS_CSRF_COOKIE_SECURE', default=True)

MIDDLEWARE += ['csp.middleware.CSPMiddleware']

CSP_DEFAULT_SRC = ("'none'")
CSP_BASE_URI = ("'self'")
CSP_CONNECT_SRC = ("'self'")
CSP_FORM_ACTION = ("'self'")
CSP_FRAME_ANCESTORS = ("'self'")
CSP_FRAME_SRC = ("'none'")
CSP_IMG_SRC = ("'self'", "data:")
CSP_MEDIA_SRC = ("'self'")
CSP_OBJECT_SRC = ("'self'")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_STYLE_SRC = ("'self'")
