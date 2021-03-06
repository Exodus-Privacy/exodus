# FAQ

## Table of contents

- [Static analysis](#static-analysis)
- [εxodus commands](#εxodus-commands)
- [Known possible issues](#known-possible-issues)

## Static analysis

### How do you detect trackers in APK?

Each tracker has its own code signatures. A code signature is basically a Java package name *e.g.* `com.google.android.apps.analytics.` and `com.google.android.gms.analytics.` are the 2 code signatures of Google Analytics.

To check if a tracker is embedded into an application, **εxodus** executes the following steps:

- download the APK from Google Play
- unzip the APK
- list Java classes which are embedded in the application (`dexdump classes*.dex`)
- save list of embedded Java classes into a file
- check if any embedded Java class matches a tracker code signature

Finding a tracker signature into an application does not prove that the tracker is effectively used by the application.

## εxodus commands

> **For all the next points, activate the εxodus virtual venv, `cd` into the same directory as `manage.py` file before executing the given command.**

### How to import trackers definitions?

```
python manage.py importtrackers --settings=exodus.settings.dev
```

Now, browse [your tracker list](http://localhost:8000/trackers/).

### How to recompute reports?

When you add a new tracker into the **εxodus** database, reports are not automatically recomputed. **εxodus** comes with few administrator commands defined [here](https://github.com/Exodus-Privacy/exodus/tree/v1/exodus/reports/management/commands).

The `refreshstaticanalysis` command has the following options:

- `--all` will take all reports in consideration. You can pass a list of report ID instead.
- `--trackers` will recompute the list of embedded trackers
- `--clist` will recompute the list of embedded Java classes

The `--clist` option is useful if you change the way you extract Java classes from an APK.

#### Refresh all reports

```
python manage.py refreshstaticanalysis --all --trackers --settings=exodus.settings.dev
```

#### Refresh only reports `2` and `4`

```
python manage.py refreshstaticanalysis 2 4 --trackers --settings=exodus.settings.dev
```

### How to dump reports?

```
python manage.py dumpdata --exclude=auth --exclude=contenttypes --exclude=authtoken --exclude=analysis_query --exclude=sessions --exclude=admin --settings=exodus.settings.production > /tmp/dump.json
```

### How to dump trackers?

```
(venv) python manage.py dumpdata trackers --settings=exodus.settings.production > /tmp/trackers.json
```

### How to count how many apps have been analysed and reports generated?

```
(venv) ~/exodus$ cd exodus/
(venv) ~/exodus/exodus$ python manage.py shell  --settings=exodus.settings.production
Python 3.5.3 (default, Jan 19 2017, 14:11:04)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from reports.models import *

In [2]: Application.objects.values('handle').distinct().count()
Out[2]: 34844

In [3]: Report.objects.all().count()
Out[3]: 38394
```

## Known possible issues

### GPlaycli refuses to download APK

It is probably a configuration issue. First of all, check the file `$HOME/.config/gplaycli/gplaycli.conf`, it should contain `android_ID=3d716411bf8bc802`

 If the issue remains, fill:

- `gmail_address`
- `gmail_password`

with a real Google Account :-(

If the file `$HOME/.config/gplaycli/gplaycli.conf` does not exist, create it and put that into:

```
[Credentials]
gmail_address=
gmail_password=
#keyring_service=gplaycli
android_ID=3d716411bf8bc802
language=en_US
token=True
token_url=https://matlink.fr/token/email/gsfid

[Cache]
token=~/.cache/gplaycli/token
```
