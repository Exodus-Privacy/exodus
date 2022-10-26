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
