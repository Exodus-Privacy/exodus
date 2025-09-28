# coding=utf-8
from __future__ import absolute_import
from .base import *
from csp.constants import NONE, SELF

default_secret_key = '9b80473f1b0c7d9f1859cfa754e40e26'
SECRET_KEY = env('EXODUS_SECRET_KEY', default=default_secret_key)

ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'
STATIC_ROOT = f'{ROOT_DIR}/staticfiles/'
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

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [NONE],
        "base-uri": [SELF],
        "connect-src": [SELF],
        "form-action": [SELF],
        "frame-ancestor": [SELF],
        "frame-src": [SELF],
        "img-src": [SELF, "data:", "https://static.exodus-privacy.eu.org"],
        "media-src": [SELF, "https://static.exodus-privacy.eu.org"],
        "object-src": [SELF],
        "script-src": [SELF, "'unsafe-inline'", "'unsafe-eval'"],
        "style-src": [SELF],
    }
}
