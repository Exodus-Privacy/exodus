# coding=utf-8
from __future__ import absolute_import
from .base import *

default_secret_key = '9b80473f1b0c7d9f1859cfa754e40e26'
SECRET_KEY = env('EXODUS_SECRET_KEY', default=default_secret_key)

ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'
STATIC_ROOT = f'{BASE_DIR}/static/'
STATICFILES_DIRS = [str(APPS_DIR / "static")]

MINIO_STORAGE_ACCESS_KEY = env('EXODUS_MINIO_ROOT_USER', default='exodusexodus')
MINIO_STORAGE_SECRET_KEY = env('EXODUS_MINIO_ROOT_PASSWORD', default='exodusexodus')

ALLOW_APK_UPLOAD = True

TRACKERS_AUTO_UPDATE = True

customization = env('EXODUS_CUSTOMIZATION', default='')
if customization:
    INSTALLED_APPS = [customization] + INSTALLED_APPS

google_username = env('EXODUS_GOOGLE_USERNAME', default='')
google_password = env('EXODUS_GOOGLE_PASSWORD', default='')
if google_username and google_password:
    GOOGLE_ACCOUNT_USERNAME = google_username
    GOOGLE_ACCOUNT_PASSWORD = google_password

CSRF_COOKIE_SECURE = env.bool('EXODUS_CSRF_COOKIE_SECURE', default=False)
