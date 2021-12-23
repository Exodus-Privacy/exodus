# REST API documentation

## Terms of use

> **This API is provided as is and Exodus Privacy or its members could not be responsive in any case.**

This API is limited to 30 requests/second (with a 50 requests burst).

:warning: If the previous limit is exceeded too many times, we will ban the originating IP address for a specific period of time.

## Authorization

**In order to use this REST API, you have to request an API key**.

### Request an API key

To do so, please send an email specifying:

* a username
* an email address (in order to tell you if something wrong has been done with your key)
* a short description of your project
* if you need more than 30 requests/second rate

Send your request to [api@exodus-privacy.eu.org](mailto:api@exodus-privacy.eu.org). Then, you will receive your API key.

### How to use it?

For clients to authenticate, the API key should be included in the `Authorization` HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:

```sh
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## API endpoints

The API is served by the URL <https://reports.exodus-privacy.eu.org/>

### Trackers

#### Get the list of trackers

`GET /api/trackers` returns `JSON`

```json
{
    "trackers": {
        "69": {
            "name": "Facebook Places",
            "network_signature": "\\.facebook\\.com",
            "code_signature": "com.facebook.places",
            "creation_date": "2017-12-05",
            "website": "https://developers.facebook.com/docs/android",
            "description": "",
            "categories": ['Analytics', 'Ads']
        },
        [edited]
    }
}
```

#### Get the number of trackers

`GET /api/trackers/count` returns `JSON`

```json
{
  "count": 400
}
```

### Applications

#### Get all analyzed applications with full details

`GET /api/applications` returns `JSON`

```json
{
  "applications": [
    {
      "id": 1,
      "handle": "com.johnson.nett",
      "name": "Calendrier des r\\u00e8gles NETT \\u00ae",
      "creator": "JOHNSON & JOHNSON SANTE BEAUTE FRANCE",
      "downloads": "50,000+ downloads",
      "app_uid": "C585E0D6274EDA2FA159542E305D2C61963BA8CC",
      "source": "google",
      "icon_phash": "103278408296944969572136665785814778239",
      "report_updated_at": 1568136675.813601
    },
    {
      "id": 2,
      "handle": "cdiscount.mobile",
      "name": "Cdiscount : N'\\u00e9conomisez pas votre plaisir",
      "creator": "Cdiscount",
      "downloads": "1,000,000+ downloads",
      "app_uid": "9F4CCA45C68B96EACD9D012F0902F406126FF660",
      "source": "google",
      "icon_phash": "320076679825009360506916699520458898952",
      "report_updated_at": 1575063216.526062
    },
    {
      "id": 3,
      "handle": "ch.hug_ge.emoteo",
      "name": "Emoteo",
      "creator": "HUG H\\u00f4pitaux universitaires de Gen\\u00e8ve",
      "downloads": "1,000+ downloads",
      "app_uid": "22ECA4EC976CC4FB11C6A0A24B2A90769E5F1A64",
      "source": "google",
      "icon_phash": "216013393868481183094163051465356731136",
      "report_updated_at": 1587278984.683278
    },
    [edited]
  ]
}
```

#### Get all analyzed applications with limited details

`GET /api/applications?option=short` returns `JSON`

```json
{
  "applications": [
    {
      "id": 1,
      "handle": "com.johnson.nett",
      "app_uid": "C585E0D6274EDA2FA159542E305D2C61963BA8CC",
      "source": "google"
    },
    {
      "id": 2,
      "handle": "cdiscount.mobile",
      "app_uid": "9F4CCA45C68B96EACD9D012F0902F406126FF660",
      "source": "google"
    },
    {
      "id": 3,
      "handle": "ch.hug_ge.emoteo",
      "app_uid": "22ECA4EC976CC4FB11C6A0A24B2A90769E5F1A64",
      "source": "google"
    },
    [edited]
  ]
}
```

#### Get the number of distinct applications

`GET /api/applications/count` returns `JSON`

```json
{
  "count": 115000
}
```

### Reports

#### Get reports of a specific application

`GET /api/search/com.app.handle` returns `JSON`
Replace `com.app.handle` with the application handle.

```json
{
    "app.greyshirts.firewall": {
        "name": "NoRoot Firewall",
        "reports": [
            {
                "updated_at": "2017-12-28T01:17:50.638Z",
                "downloads": "1,000,000+ downloads",
                "trackers": [27],
                "creation_date": "2017-12-28T01:17:50.605Z",
                "version_code": "41",
                "version": "3.0.1",
                "source": "google",
                "id": 57
            }
        ],
        "creator": "Grey Shirts"
    }
}
```

#### Get flatten detailed reports for a given handle

`GET /api/search/com.app.handle/details` returns `JSON`
Replace `com.app.handle` with the application handle.

```json
[{
  "handle": "org.smssecure.smssecure",
  "app_name": "",
  "uaid": "A3509D616FEEF571171CFF5FA2C5E52AB14B0F2E",
  "version_name": "0.15.8",
  "version_code": "137",
  "source": "google",
  "icon_hash": "133488413146636779444378132657184449536",
  "apk_hash": "a0725666e702b76653dc600430a7e87ecee9e9e7c07c02a88391bcbf60adb652",
  "created": "2017-11-24T17:06:54.048Z",
  "updated": "2021-03-13T15:56:54.357Z",
  "report": 380,
  "creator": "",
  "downloads": "",
  "trackers": [],
  "permissions": [
    "org.smssecure.smssecure.ACCESS_SECRETS",
    "android.permission.READ_PROFILE",
    "android.permission.WRITE_PROFILE",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.RECEIVE_SMS",
    "android.permission.RECEIVE_MMS",
    "android.permission.READ_SMS",
    "android.permission.SEND_SMS",
    "android.permission.WRITE_SMS",
    "android.permission.VIBRATE",
    "android.permission.ACCESS_NETWORK_STATE",
    "android.permission.CHANGE_NETWORK_STATE",
    "android.permission.READ_PHONE_STATE",
    "android.permission.WAKE_LOCK",
    "android.permission.INTERNET",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.READ_EXTERNAL_STORAGE"
  ]
},
...]
```

#### Get the number of reports

`GET /api/reports/count` returns `JSON`

```json
{
  "count": 225000
}
```
