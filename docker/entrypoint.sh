#!/bin/bash

declare -Ar commandList=(
	[compile-messages]=compileMessages
	[create-db]=createDb
	[create-user]=createUser
	[import-trackers]=importTrackers
	[init]=init
	[make-messages]=makeMessages
	[refresh-fdroid-index]=refreshFdroidIndex
	[start-frontend]=startFrontEnd
	[start-worker]=startWorker
)

declare -Ar commandHelpList=(
	[compile-messages]='compile translation messages'
	[create-db]='create database if required and attend to migrations'
	[create-user]='actually create a super user if not created yet'
	[import-trackers]='import trackers from the official exodus instance'
	[init]='Initialize database and launch Exodus'
	[make-messages]='extract translation messages'
	[refresh-fdroid-index]='fetch F-Droids list of packages'
	[start-frontend]='lauch the local front end'
	[start-worker]='start the exodus worker'
)

function main()
{
	getSettings
	if [ -z "$1" ]
	then
		usage "$0"
	elif [ -n "${commandList[$1]}" ]
	then
		"${commandList[$1]}"
	else
		exec "$@"
	fi
}

function usage()
{
	cat <<- EOS
		$1: prepare and lauch exodus

	EOS

	for cmd in "${!commandHelpList[@]}"
	do
		cat <<- EOS
			$cmd: ${commandHelpList[$cmd]}
		EOS
	done
}

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

main "$@"
