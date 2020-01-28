# coding=utf-8
import os

DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DIR)

INSTALLED_APPS = [
    'web',
    'analysis_query.apps.AnalysisQueryConfig',
    'trackers.apps.TrackersConfig',
    'trackers.templatetags',
    'reports.apps.ReportsConfig',
    'restful_api.apps.RestfulApiConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django_celery_beat',
    'minio_storage',
    'eventlog.apps.EventLogConfig',
    'rest_framework',
    'rest_framework.authtoken',
]

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('es', 'Español'),
]

DEFAULT_LANGUAGE = 1

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'exodus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./exodus/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'exodus.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# File storage
EX_FS_ROOT = os.path.join(BASE_DIR, "..", "storage")
EX_APK_FS_ROOT = os.path.join(EX_FS_ROOT, "apks")
EX_NET_FS_ROOT = os.path.join(EX_FS_ROOT, "net")
# Celery
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'

EX_PAGINATOR_COUNT = 25

LOCALE_PATHS = (os.path.join(DIR, '../locale'),)

TRACKERS_AUTO_UPDATE = False
TRACKERS_AUTO_UPDATE_TIME = 4 * 24 * 60 * 60.0  # time in seconds
TRACKERS_AUTO_UPDATE_FROM = 'https://reports.exodus-privacy.eu.org/api/trackers'

ANALYSIS_REQUESTS_AUTO_CLEANUP_TIME = 24 * 60 * 60.0  # time in seconds
ANALYSIS_REQUESTS_KEEP_DURATION = 4  # time in days

# Minio file storage configuration
DEFAULT_FILE_STORAGE = 'minio_storage.storage.MinioMediaStorage'
MINIO_STORAGE_ENDPOINT = '127.0.0.1:9000'
MINIO_STORAGE_ACCESS_KEY = 'access_key'
MINIO_STORAGE_SECRET_KEY = 'secret_key'
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = 'exodus'
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True

# Analysis configuration
ALLOW_APK_UPLOAD = False
