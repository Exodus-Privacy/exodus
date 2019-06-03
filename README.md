# εxodus

**εxodus** is a privacy auditing platform for Android applications. It detects behaviors which can be dangerous for user privacy like ads, tracking, analytics, …

The official instance of εxodus is available [here](https://reports.exodus-privacy.eu.org/).

## Contribute to the identification of trackers

All data about trackers are stored on [ETIP](https://etip.exodus-privacy.eu.org) (εxodus tracker investigation platform).

If you wish to help us identify new trackers, you can request an ETIP account by sending a username and an email address to [etip@exodus-privacy.eu.org](mailto:etip@exodus-privacy.eu.org)

## Getting Started

### Installing

You have 3 different ways of setting up your development environment:

- [Manual](doc/install/manual.md)
- [Docker](doc/install/docker.md)
- [Vagrant](doc/install/vagrant.md)

### Analyzing an application

Browse to [the analysis submission page](http://127.0.0.1:8000/analysis/submit/) and start a new analysis (ex: `fr.meteo`).
When the analysis is finished, compare the results with the same report from [the official instance](https://reports.exodus-privacy.eu.org).

### FAQ

Check the [FAQ](doc/faq.md) if you encounter any problem or need an extended documentation about εxodus.

## API documentation

You can find the εxodus API documentation [here](doc/api.md).

## License

This project is licensed under the GNU AGPL v3 License - see the [LICENSE](LICENSE) file for details.
