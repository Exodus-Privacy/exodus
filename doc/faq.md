# FAQ

## GPlaycli refuses to download APK
It is probably a configuration issue. First of all, check the file `$HOME/.config/gplaycli/gplaycli.conf`, it
should contains:
  * `android_ID=3d716411bf8bc802`

 If the issue remains, fill:
   * `gmail_address`
   * `gmail_password`

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

## How to import trackers definitions?
We periodically export trackers definitions from the poduction instance. This export is a JSON file you can easily import using Django admin.
To do so, get trackers definition from [production](https://y.0x39b.fr/zerobin/?b8cd1e442301940d#HCuV45xNQ/MAPvHVFifCr0tdoX7dxP7f2H55JXc1PHg=) by clicking on *Raw text* and copying the content into a json file, for example in `/tmp/trackers.json`.
Once saved, activate the εxodus virtual venv, `cd` into the same directory as `manage.py` file and execute the following command:
```bash
python manage.py loaddata /tmp/trackers.json --settings=exodus.settings.dev
```
Django should say something like
```
Installed 71 object(s) from 1 fixture(s)
```
Now, browse [your tracker list](http://localhost:8000/trackers/).

## Read `.pcap` files  as simple user
```bash
chmod g+s net
```
