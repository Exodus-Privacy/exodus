source ../venv/bin/activate
export DJANGO_SETTINGS_MODULE=exodus.settings.production
python manage.py celery worker -A exodus.core -l info