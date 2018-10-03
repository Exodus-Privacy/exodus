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
Activate the εxodus virtual venv, `cd` into the same directory as `manage.py` file and execute the following command:
```bash
python manage.py importtrackers --settings=exodus.settings.dev
```

Now, browse [your tracker list](http://localhost:8000/trackers/).

## Read `.pcap` files  as simple user
```bash
chmod g+s net
```
