# εxodus
**εxodus** is a privacy auditing platform for Android applications. It detects behaviors which can be 
dangerous for user privacy like ads, tracking, analytics, … 

The official instance of εxodus is available [here](https://reports.exodus-privacy.eu.org/).

# Development environment

## Docker

Run dependencies:

```
docker-compose up -d
```

Run εxodus container:

```
docker-compose -f docker-compose.run.yml up -d
```

Create database, user and import trackers:
```
docker exec -it <εxodus_container> /entrypoint.sh "create-db"
docker exec -it <εxodus_container> /entrypoint.sh "create-user"
docker exec -it <εxodus_container> /entrypoint.sh "import-trackers"
```

Run worker and frontend:
```
docker exec -it <εxodus_container> /entrypoint.sh "start-worker"
docker exec -it <εxodus_container> /entrypoint.sh "start-frontend"
```


## Vagrant

Install [vagrant](https://www.vagrantup.com/) and [ansible](https://www.ansible.com/) then execute:

```
vagrant up
```

Now, you can [make a tea](https://wiki.laquadrature.net/TeaHouse).

Or you can follow the [step by step installation](doc/install.md) guide. Check the [FAQ](doc/faq.md) if you encounter problem.

# Analyse an application

Browse [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and enter your login and password. Then,
browse [http://127.0.0.1:8000/analysis/submit/](http://127.0.0.1:8000/analysis/submit/), specify an application handle
and click on submit.
