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

#### Requirements

- docker
- docker-compose

#### Prepare your settings

You can tweak your instance by changing [some settings](#configuring-your-local-instance).

Create the file  `exodus/exodus/settings/custom_docker.py` with the following content:

```bash
from .docker import *

GOOGLE_ACCOUNT_USERNAME = "<a valid google account>"
GOOGLE_ACCOUNT_PASSWORD = "<a valid google password>"

# Overwrite any other settings you wish to
```

#### Run

```bash
echo uid=$(id -u) > .env
docker-compose up -d
# Once exodus started, you can check its logs
docker-compose logs -f exodus-front
```

When everything is up (Docker logs `Exodus DB is ready.`), you may have to force a first download of the F-Droid index:

```bash
docker-compose exec exodus-worker /entrypoint.sh refresh-fdroid-index
```

**The worker must be running** to do this.

The exodus container automatically:

- Create the database
- Make migration
- Import trackers from the main instance
- Start the frontend of exodus

Don't forget to rebuild your image and refresh your container if there is any change with `docker-compose up -d --build`.

#### Aliases

You can use the command

```bash
docker-compose exec exodus-worker /entrypoint.sh "<command>"
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

This setup is based on a Debian 11 (Bullseye) configuration.

#### 1 - Install system dependencies

```bash
sudo apt install git virtualenv postgresql-13 rabbitmq-server build-essential libssl-dev dexdump libffi-dev python3-dev libxml2-dev libxslt1-dev
```

#### 2 - Clone the project

```bash
git clone https://github.com/Exodus-Privacy/exodus.git
```

#### 3 - Create database and user

```bash
sudo su - postgres
psql
CREATE USER exodus WITH PASSWORD 'exodus';
CREATE DATABASE exodus WITH OWNER exodus;
\c exodus
CREATE EXTENSION pg_trgm;
```

#### 4 - Set Python virtual environment and install dependencies

```bash
cd exodus
virtualenv ./venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

#### 4b - Patch gpapi

```bash
# See https://github.com/NoMore201/googleplay-api/pull/145
cp gpapi/googleplay.py venv/lib/python3/site-packages/gpapi/googleplay.py
# See https://github.com/NoMore201/googleplay-api/pull/153
cp gpapi/config.py venv/lib/python3/site-packages/gpapi/config.py
```

#### 5 - Create the DB schema

```bash
cd exodus
python manage.py migrate --fake-initial --settings=exodus.settings.dev
python manage.py makemigrations --settings=exodus.settings.dev
python manage.py migrate --settings=exodus.settings.dev
```

#### 6 - Create admin user

You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.

```bash
source venv/bin/activate
cd exodus
python manage.py createsuperuser --settings=exodus.settings.dev
```

#### 7 - Install Minio server

Minio is in charge to store files like APK, icons, flow and pcap files.

```bash
wget https://dl.minio.io/server/minio/release/linux-amd64/minio -O $HOME/minio
chmod +x $HOME/minio
```

**Configure Minio**

```bash
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

```bash
mkdir -p /tmp/exodus-storage
```

#### 8 - Start Minio

```bash
$HOME/minio server /tmp/exodus-storage --console-address :9001
```

Minio API is now listening on `9000` port and the browser interface is available
at [http://127.0.0.1:9001](http://127.0.0.1:9001). Use `exodusexodus` as both login
and password.

#### 9 - Configure your instance

You can tweak your instance by changing [some settings](#configuring-your-local-instance).

Create the file  `exodus/exodus/settings/custom_dev.py` with the following content:

```bash
from .dev import *

GOOGLE_ACCOUNT_USERNAME = "<a valid google account>"
GOOGLE_ACCOUNT_PASSWORD = "<a valid google password>"

# Overwrite any other settings you wish to
```

#### 10 - Start the εxodus worker and scheduler

The εxodus handle asynchronous tasks submitted by the front-end.
You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.

```bash
source venv/bin/activate
cd exodus

export DJANGO_SETTINGS_MODULE=exodus.settings.custom_dev; celery -A exodus.core worker --beat -l debug -S django
```

Now, the εxodus worker and scheduler are waiting for tasks.

#### 11 - Start the εxodus front-end

You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.

```bash
source venv/bin/activate
cd exodus
python manage.py runserver --settings=exodus.settings.custom_dev
```

Now browse [http://127.0.0.1:8000](http://127.0.0.1:8000)

#### 12 - Import the trackers definitions

Activate the εxodus virtual venv, `cd` into the same directory as `manage.py` file and execute the following commands:

```bash
python manage.py import_categories --settings=exodus.settings.custom_dev
python manage.py importtrackers --settings=exodus.settings.custom_dev
```

Now, browse [your tracker list](http://127.0.0.1:8000/trackers/)

#### 13 - Get the F-droid index data

An initial F-droid index manual download may be required:

```bash
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
| DISABLE_SUBMISSIONS                 | Whether to disable app submissions           | False           |
| GOOGLE_ACCOUNT_USERNAME             | Username for Google account to download apps | /               |
| GOOGLE_ACCOUNT_PASSWORD             | Password for Google account to download apps | /               |

## Analyzing an application

Browse to [the analysis submission page](http://127.0.0.1:8000/analysis/submit/) and start a new analysis (ex: `fr.meteo`).
When the analysis is finished, compare the results with the same report from [the official instance](https://reports.exodus-privacy.eu.org).
