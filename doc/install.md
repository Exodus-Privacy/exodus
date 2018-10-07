# Development environment
## Step 1 - System dependencies
```
sudo apt install git virtualenv postgresql-9.6 rabbitmq-server tshark aapt build-essential libssl-dev dexdump libffi-dev python3-dev openjdk-8-jre libxml2-dev libxslt1-dev
```

## Step 2 - Clone the project
```
git clone https://github.com/Exodus-Privacy/exodus.git
```

## Step 3 - Create database and user
```
sudo su - postgres
psql
CREATE USER exodus WITH PASSWORD 'exodus';
CREATE DATABASE exodus WITH OWNER exodus;
```

## Step 4 - Set Python virtual environment and install dependencies
```
cd exodus
virtualenv ./venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

## Step 5 - Create the DB schema
```
cd exodus
python manage.py migrate --fake-initial --settings=exodus.settings.dev
python manage.py makemigrations --settings=exodus.settings.dev
python manage.py migrate --settings=exodus.settings.dev
```

## Step 6 - Create admin user
You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.
```
source venv/bin/activate
cd exodus
python manage.py createsuperuser --settings=exodus.settings.dev
```

## Step 7 - Install Minio server
Minio is in charge to store files like APK, icons, flow and pcap files.
```
wget https://dl.minio.io/server/minio/release/linux-amd64/minio -O $HOME/minio
chmod +x $HOME/minio
```
### Configure Minio
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

### Create Minio storage location
```
mkdir -p /tmp/exodus-storage
```

## Step 8 - Start Minio
```
$HOME/minio server /tmp/exodus-storage
```
Minio is now listening on `9000` port and the browser interface is available
at [http://127.0.0.1:9000](http://127.0.0.1:9000). Use `exodusexodus` as both login
and password.

## Step 9 - Start the εxodus worker
The εxodus handle asynchronous tasks submitted by the front-end.
You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.
```
source venv/bin/activate
cd exodus

export DJANGO_SETTINGS_MODULE=exodus.settings.dev; python manage.py celery worker -A exodus.core -l info
```
Now, the εxodus worker is waiting for tasks.

## Step 10 - Start the εxodus front-end
You have to activate the virtual venv and `cd` into the same directory as `manage.py` file.
```
source venv/bin/activate
mkdir -p $HOME/.config/gplaycli/
cp venv/lib/python3.5/site-packages/$HOME/.config/gplaycli/gplaycli.conf $HOME/.config/gplaycli/gplaycli.conf
cd exodus
python manage.py runserver --settings=exodus.settings.dev
```
Now browse [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Step 11 - Import the trackers definitions
Activate the εxodus virtual venv, `cd` into the same directory as `manage.py` file and execute the following command:
```
python manage.py importtrackers --settings=exodus.settings.dev
```
Now, browse [your tracker list](http://127.0.0.1:8000/trackers/)

## Step 12 - Submit an analysis
Browse [the analysis submission page](http://127.0.0.1:8000/analysis/submit/) and start a new analysis (ex: fr.meteo).
When the analysis is finished, compare the results with the same report from [the official instance](https://reports.exodus-privacy.eu.org).
