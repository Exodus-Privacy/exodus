# Exodus
**Exodus** is meant to:
  * download a bunch of APK files from *Google Play*
  * find trackers signature in unzipped APK
  * retreive application information like version, handle, ...
  * manage Android VirtualBox VM
  * install and run Android applications
  * analyze the network traffic generated by the application
  * retreive DNS queries and responses
  * retreive HTTP posted data
  * generate JSON report

# Deploy
## System dependencies
```
sudo apt install git virtualenv postgresql-9.6 rabbitmq-server aapt build-essential libssl-dev libffi-dev python-dev openjdk-8-jre
```

## Clone the project
```
git clone -b v1 ssh://<username>@62.210.131.96:19100/data/depots/exodus/exodus.git Exodus
```

## Create database
```
sudo su - postgres
psql
CREATE USER exodus WITH PASSWORD 'a big password';
CREATE DATABASE exodus WITH OWNER exodus;
```
Set the password in the file `Exodus/exodus/exodus/settings.py` line 97.

## Set Python virtual environement and dependencies   
```
cd Exodus
virtualenv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

## Create the DB schema
```
cd exodus/exodus
python manage.py migrate --fake-initial
python manage.py migrate
```

## Create admin user
```
python manage.py createsuperuser
```

# Electra
## Install Android 7.1 (deprecated)
Download the ISO of Android 7.1 x86_64 : 
```
torify wget https://osdn.net/frs/redir.php?m=rwthaachen&f=%2Fandroid-x86%2F67834%2Fandroid-x86_64-7.1-rc1.iso
```
Create a new VM and set: 
```
Pointer device : PS/2
```
Set `bridge` network mode.
Specify the shitty GMail account.
Install the FakeGPS application.
Create a snapshot

## Install Android 6.0
See https://www.osboxes.org/android-x86/
Set `bridge` network mode.
Specify the shitty GMail account.
Install the FakeGPS application.
Create a snapshot

## Configure ADB
In Android terminal emulator
```
su
setprop service.adb.tcp.port 5555
stop adbd
start adbd
ifconfig
```

# ToDo
  * add geo-tagged pictures in Android custom build


# Notes
## Run `tcpdump` as simple user
```bash
sudo visudo
```
and append the following line before the `include ...` one at the bottom of the file
```
<usename>  ALL=(ALL) NOPASSWD: /usr/sbin/tcpdump
```

## Read `.pcap` files  as simple user
```bash
chmod g+s net
```