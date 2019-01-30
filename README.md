# εxodus
**εxodus** is a privacy auditing platform for Android applications. It detects behaviors which can be
dangerous for user privacy like ads, tracking, analytics, …

The official instance of εxodus is available [here](https://reports.exodus-privacy.eu.org/).

## Contribute to the identification of trackers

All the data about trackers are stored on [ETIP](https://etip.exodus-privacy.eu.org) (εxodus tracker investigation platform).

If you wish to help us identify new trackers, you can request an ETIP account by sending a pseudonym and an email address to etip@exodus-privacy.eu.org

## Development environment

You have 3 different ways of setting up your development environment (Docker, Vagrant or manual).
Check the [FAQ](doc/faq.md) if you encounter problem.

### Docker

Follow the [Docker setup](doc/docker.md) guide.

### Vagrant

Install [vagrant](https://www.vagrantup.com/) and [ansible](https://www.ansible.com/) then execute:

```
vagrant up
```

Now, you can [make a tea](https://wiki.laquadrature.net/TeaHouse).

### Manual installation

Follow the [step by step installation](doc/install.md) guide.

### Analyse an application

Browse [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and enter your login and password. Then,
browse [http://127.0.0.1:8000/analysis/submit/](http://127.0.0.1:8000/analysis/submit/), specify an application handle
and click on submit.
