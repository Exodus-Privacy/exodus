#!/bin/bash

EXODUS_HOME="/exodus"

function createDB() {
	cd ${EXODUS_HOME}/exodus/
	echo 'CREATE EXTENSION IF NOT EXISTS pg_trgm;' | python3 manage.py dbshell --settings=exodus.settings.docker
	python3 manage.py makemigrations --settings=exodus.settings.docker
	python3 manage.py migrate --settings=exodus.settings.docker
}

function createUser() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py createsuperuser --settings=exodus.settings.docker
}

function startWorker() {
	cd ${EXODUS_HOME}/exodus/
	export DJANGO_SETTINGS_MODULE=exodus.settings.docker; export C_FORCE_ROOT=1; celery worker -A exodus.core -l info
}

function startFrontend() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py runserver --settings=exodus.settings.docker 0.0.0.0:8000
}

function importTrackers() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py importtrackers --settings=exodus.settings.docker
}

function makeMessages() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py makemessages --settings=exodus.settings.docker
}

function compileMessages() {
	cd ${EXODUS_HOME}/exodus/
	python3 manage.py compilemessages --settings=exodus.settings.docker
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

function createGplaycliConfiguration() {
	sed -e "s/GOOGLE_ACCOUNT_USERNAME/${1}/g;s/GOOGLE_ACCOUNT_PASSWORD/${2}/g;s/USE_TOKEN_DISPENSER/${3}/g;s@TOKEN_DISPENSER_URL@${4}@g" /home/exodus/.config/gplaycli/docker.gplaycli.conf > /home/exodus/.config/gplaycli/gplaycli.conf
}

case "${1}" in
	"init")
		createGplaycliConfiguration ${GOOGLE_ACCOUNT_USERNAME} ${GOOGLE_ACCOUNT_PASSWORD} ${USE_TOKEN_DISPENSER} ${TOKEN_DISPENSER_URL}
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
	"make-messages")
		makeMessages
		;;
	"compile-messages")
		compileMessages
		;;
esac
