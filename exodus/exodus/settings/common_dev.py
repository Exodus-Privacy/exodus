# coding=utf-8
from __future__ import absolute_import
from .base import *

default_secret_key = '9b80473f1b0c7d9f1859cfa754e40e26'
SECRET_KEY = os.environ.get('EXODUS_SECRET_KEY', default_secret_key)

DEBUG = True
ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, '..', 'static'), )

MINIO_STORAGE_ACCESS_KEY = os.environ.get('EXODUS_MINIO_ACCESS_KEY', 'exodusexodus')
MINIO_STORAGE_SECRET_KEY = os.environ.get('EXODUS_MINIO_SECRET_KEY', 'exodusexodus')

ALLOW_APK_UPLOAD = True

TRACKERS_AUTO_UPDATE = True

customization = os.environ.get('EXODUS_CUSTOMIZATION')
if customization:
    INSTALLED_APPS = [customization] + INSTALLED_APPS

google_username = os.environ.get('EXODUS_GOOGLE_USERNAME')
google_password = os.environ.get('EXODUS_GOOGLE_PASSWORD')
if google_username and google_password:
    GOOGLE_ACCOUNT_USERNAME = google_username
    GOOGLE_ACCOUNT_PASSWORD = google_password
