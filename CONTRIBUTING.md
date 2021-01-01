# Contributing

## Looking for something you can do?

You can find our list of [issues](https://github.com/Exodus-Privacy/exodus/issues) and in particular the ones with the tag ["good first issue"](https://github.com/Exodus-Privacy/exodus/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) or ["hacktoberfest"](https://github.com/Exodus-Privacy/exodus/issues?q=is%3Aissue+is%3Aopen+label%3Ahacktoberfest)

[Documentation](doc/install.md) is available to help you set up your local instance.

## What you need to respect

### Code of conduct

Please follow [Exodus Privacy's code of conduct](https://exodus-privacy.eu.org/en/page/who/)

### Tests

You need to make sure your changes do not break the existing tests.

You can execute the tests with the following command:

```
source venv/bin/activate
cd exodus
python manage.py test --settings=exodus.settings.dev
```

If you are adding a new feature, it's deeply appreciated if you can write tests for it :)

### Linter

The following linters are used:

* [flake8](https://pypi.org/project/flake8/) for the python code
* [hadolint](https://github.com/hadolint/hadolint) for the Docker image

[LGTM](https://lgtm.com) is also run on each new Pull Requests.
