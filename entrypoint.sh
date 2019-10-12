#!/bin/bash

EXODUS_HOME="/home/exodus/exodus"

function createDB() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py makemigrations --settings=exodus.settings.docker
	python3 manage.py migrate --settings=exodus.settings.docker
}

function createUser() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py createsuperuser --settings=exodus.settings.docker
}

function startWorker() {
	cd ${EXODUS_HOME}/exodus/
	export DJANGO_SETTINGS_MODULE=exodus.settings.docker; python3 manage.py celery worker -A exodus.core -l info
}

function startFrontend() {
	cp /usr/local/lib/python3.5/site-packages/root/.config/gplaycli/gplaycli.conf /home/exodus/.config/gplaycli/gplaycli.conf
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py runserver --settings=exodus.settings.docker 0.0.0.0:8000
}

function importTrackers() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py importtrackers --settings=exodus.settings.docker
}

function init() {
	while ! pg_isready -h db -p 5432 > /dev/null 2> /dev/null; do
		echo "Connecting to db (postgresql) Failed: Waiting ..."
    	sleep 1
	done
	createDB
	importTrackers
	echo "Exodus is ready."
	startFrontend
}

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
esac

