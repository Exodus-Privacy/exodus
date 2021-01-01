#!/bin/bash

function getSettings() {
    if [ -f "/exodus/exodus/exodus/settings/custom_docker.py" ]; then
        export DJANGO_SETTINGS_MODULE=exodus.settings.custom_docker
    else
        export DJANGO_SETTINGS_MODULE=exodus.settings.docker
    fi
}

function createDB() {
    echo 'CREATE EXTENSION IF NOT EXISTS pg_trgm;' | python3 manage.py dbshell
    python3 manage.py makemigrations
    python3 manage.py migrate
}

function createUser() {
    python3 manage.py createsuperuser
}

function startWorker() {
    export C_FORCE_ROOT=1; celery worker --beat -A exodus.core -l info -S django
}

function startFrontend() {
    python3 manage.py runserver 0.0.0.0:8000
}

function importTrackers() {
    python3 manage.py import_categories
    python3 manage.py importtrackers
}

function makeMessages() {
    python3 manage.py makemessages
}

function compileMessages() {
    python3 manage.py compilemessages
}

function refreshFdroidIndex() {
    python3 manage.py refresh_fdroid_index
}

function init_db() {
    while ! pg_isready -h db -p 5432 > /dev/null 2> /dev/null; do
        echo "Connecting to db (postgresql) Failed: Waiting ..."
        sleep 1
    done
    createDB
    importTrackers
    echo "Exodus DB is ready."
}

function init() {
    init_db
    startFrontend
}

getSettings

case "${1}" in
    "init")
        init
        ;;
    "create-db")
        createDB
        ;;
    "create-user")
        createUser
        ;;
    "start-worker")
        startWorker
        ;;
    "start-frontend")
        startFrontend
        ;;
    "import-trackers")
        importTrackers
        ;;
    "refresh-fdroid-index")
        refreshFdroidIndex
        ;;
    "make-messages")
        makeMessages
        ;;
    "compile-messages")
        compileMessages
        ;;
esac
