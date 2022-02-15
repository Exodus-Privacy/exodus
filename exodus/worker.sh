source ../venv/bin/activate
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-exodus.settings.production}
celery -A exodus.core worker -l info
