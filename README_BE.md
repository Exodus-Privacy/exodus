## Installation
```
sudo apt install virtualenv postgresql-9.6 rabbitmq-server
virtualenv ./venv
source venv/bin/activate
pip install -r requirements.txt
sudo su - postgres
psql
CREATE USER exodus WITH PASSWORD '82b0a4e31030851dd88fba45715bbf558ba73e44140439c0f42113904806bdea';
CREATE DATABASE exodus WITH OWNER exodus;
Ctrl+D
Ctrl+D
python manage.py migrate --fake-initial
python manage.py migrate
python manage.py createsuperuser
```
