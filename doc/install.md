# Getting Started

- [Installing your development environment](#installing-your-development-environment)
- [Configuring your local instance](#configuring-your-local-instance)
- [Analyzing an application](#analyzing-an-application)

## Installing your development environment

You have different ways of setting up your development environment:

- [Docker](#docker-setup)
- [Manual](#manual-setup)
- ~~Vagrant (Deprecated)~~

### Docker setup

#### Run

Edit `docker-compose.yml` (set a Google account username and password).

```bash
docker-compose up -d
docker logs -f exodus
```

When everything is up (Docker logs `Exodus is ready.`), launch the worker:
```bash
docker exec -it exodus /entrypoint.sh "start-worker"
```

Then, force a first download of the F-Droid index, the worker **must be** running (with previous command) to do this:
```bash
docker exec -it exodus /entrypoint.sh "refresh-fdroid-index"
```

The exodus container automatically:
- Create the database
- Make migration
- Import trackers from the main instance
- Start the frontend of exodus

Don't forget to rebuild your container if there is any change with `docker-compose build`.

#### Aliases

You can use the command
```bash
docker exec -it exodus /entrypoint.sh "<command>"
```
to make actions, where `<command>` can be:
- `compile-messages`: Compile the translation messages
- `create-db`: Create the database and apply migrations
- `create-user`: Create a Django user
- `make-messages`: Create the extracted translation messages
- `import-trackers`: Import all trackers from the main exodus instance
- `start-frontend`: Start the web server
- `start-worker`: Start the exodus worker
- `refresh-fdroid-index`: Refresh F-Droid index file

### Manual setup

#### 1 - Install system dependencies

```
sudo apt install git virtualenv postgresql-9.6 rabbitmq-server tshark aapt build-essential libssl-dev dexdump libffi-dev python3-dev openjdk-8-jre libxml2-dev libxslt1-dev
```

#### 2 - Clone the project

```
git clone https://github.com/Exodus-Privacy/exodus.git
```

#### 3 - Create database and user

```
sudo su - postgres
psql
CREATE USER exodus WITH PASSWORD 'exodus';
CREATE DATABASE exodus WITH OWNER exodus;
\c exodus
CREATE EXTENSION pg_trgm;
```

#### 4 - Set Python virtual environment and install dependencies

```
cd exodus
virtualenv ./venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

#### 5 - Create the DB schema

```
cd exodus
python manage.py migrate --fake-initial --settings=exodus.settings.dev
python manage.py makemigrations --settings=exodus.settings.dev
python manage.py migrate --settings=exodus.settings.dev
```

#### 6 - Create admin user

You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.
```
source venv/bin/activate
cd exodus
python manage.py createsuperuser --settings=exodus.settings.dev
```

#### 7 - Install Minio server

Minio is in charge to store files like APK, icons, flow and pcap files.
```
wget https://dl.minio.io/server/minio/release/linux-amd64/minio -O $HOME/minio
chmod +x $HOME/minio
```

**Configure Minio**

```
mkdir -p $HOME/.minio
cat > $HOME/.minio/config.json << EOL
{
        "version": "20",
        "credential": {
                "accessKey": "exodusexodus",
                "secretKey": "exodusexodus"
        },
        "region": "",
        "browser": "on",
        "logger": {
                "console": {
                        "enable": true
                },
                "file": {
                        "enable": false,
                        "filename": ""
                }
        },
        "notify": {}
}
EOL
```

**Create Minio storage location**

```
mkdir -p /tmp/exodus-storage
```

#### 8 - Start Minio

```
$HOME/minio server /tmp/exodus-storage
```
Minio is now listening on `9000` port and the browser interface is available
at [http://127.0.0.1:9000](http://127.0.0.1:9000). Use `exodusexodus` as both login
and password.

#### 9 - Configure your instance

You can tweak your instance by changing [some settings](#configuring-your-local-instance).

Create the file  `exodus/exodus/settings/custom_dev.py` with the following content:
```
from .dev import *

GOOGLE_ACCOUNT_USERNAME = "<a valid google account>"
GOOGLE_ACCOUNT_PASSWORD = "<a valid google password>"

# Overwrite any other settings you wish to
```

#### 10 - Start the εxodus worker and scheduler

The εxodus handle asynchronous tasks submitted by the front-end.
You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.
```
source venv/bin/activate
cd exodus

export DJANGO_SETTINGS_MODULE=exodus.settings.custom_dev; celery worker --beat -A exodus.core -l debug -S django
```
Now, the εxodus worker and scheduler are waiting for tasks.

#### 11 - Start the εxodus front-end

You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.
```
source venv/bin/activate
mkdir -p $HOME/.config/gplaycli/
cp venv/lib/python3.5/site-packages/$HOME/.config/gplaycli/gplaycli.conf $HOME/.config/gplaycli/gplaycli.conf
cd exodus
python manage.py runserver --settings=exodus.settings.custom_dev
```
Now browse [http://127.0.0.1:8000](http://127.0.0.1:8000)

#### 12 - Import the trackers definitions

Activate the εxodus virtual venv, `cd` into the same directory as `manage.py` file and execute the following commands:
```
python manage.py import_categories --settings=exodus.settings.custom_dev
python manage.py importtrackers --settings=exodus.settings.custom_dev
```
Now, browse [your tracker list](http://127.0.0.1:8000/trackers/)

#### 13 - Get the F-droid index data

An initial F-droid index manual download may be required:
```
python manage.py refresh_fdroid_index --settings=exodus.settings.custom_dev
```

## Configuring your local instance

The following options can be configured in `exodus/exodus/settings/`:

| Setting                             | Description                                  | Default         |
|-------------------------------------|----------------------------------------------|-----------------|
| EX_PAGINATOR_COUNT                  | Number of elements per page                  | 25              |
| TRACKERS_AUTO_UPDATE                | Whether to update automatically trackers     | False           |
| TRACKERS_AUTO_UPDATE_TIME           | Trackers update frequency (in seconds)       | 345600          |
| TRACKERS_AUTO_UPDATE_FROM           | Exodus instance to update trackers from      | <live instance> |
| ANALYSIS_REQUESTS_AUTO_CLEANUP_TIME | Requests cleanup frequency (in seconds)      | 86400           |
| ANALYSIS_REQUESTS_KEEP_DURATION     | Requests keep duration (in days)             | 4               |
| ALLOW_APK_UPLOAD                    | Whether to allow APK file upload             | False           |
| GOOGLE_ACCOUNT_USERNAME             | Username for Google account to download apps | /               |
| GOOGLE_ACCOUNT_PASSWORD             | Password for Google account to download apps | /               |

## Analyzing an application

Browse to [the analysis submission page](http://127.0.0.1:8000/analysis/submit/) and start a new analysis (ex: `fr.meteo`).
When the analysis is finished, compare the results with the same report from [the official instance](https://reports.exodus-privacy.eu.org).
