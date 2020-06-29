# REST API documentation

## Terms of use

> **This API is provided as is and Exodus Privacy or its members could not be responsive in any case.**

## API key

**In order to use this REST API, you have to request an API key**. To do so, please send an email specifying:
* a username
* an email address (in order to tell you if something wrong has been done with your key)
* a short description of your project

Send your request to [bureau@exodus-privacy.eu.org](mailto:bureau@exodus-privacy.eu.org). Then, you will receive your API key.

### How to use it?

For clients to authenticate, the API key should be included in the `Authorization` HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Get the list of trackers

`GET` https://reports.exodus-privacy.eu.org/api/trackers returns `JSON`
```
{
    "trackers": {
        "69": {
            "name": "Facebook Places",
            "network_signature": "\\.facebook\\.com",
            "code_signature": "com.facebook.places",
            "creation_date": "2017-12-05",
            "website": "https://developers.facebook.com/docs/android",
            "description": ""
        },
        [edited]
    }
}
```

## Get all analyzed applications

### With full details

`GET` https://reports.exodus-privacy.eu.org/api/applications returns `JSON`
```
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

### With limited details

`GET` https://reports.exodus-privacy.eu.org/api/applications?option=short returns `JSON`
```
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

## Get reports of a specific application

`GET` https://reports.exodus-privacy.eu.org/api/search/com.app.handle returns `JSON`
Replace `com.app.handle` with the application handle.
```
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
                "id": 57
            }
        ],
        "creator": "Grey Shirts"
    }
}
```
## Get flatten detailed reports for a given handle

`GET` https://reports.exodus-privacy.eu.org/api/search/com.app.handle/details returns `JSON`
Replace `com.app.handle` with the application handle.
```
[{
  "uaid": "A3509D616FEEF571171CFF5FA2C5E52AB14B0F2E",
  "updated": "2018-08-16T16:53:11.575Z",
  "apk_hash": "a0725666e702b76653dc600430a7e87ecee9e9e7c07c02a88391bcbf60adb652",
  "downloads": "",
  "version_code": "137",
  "report": 380,
  "created": "2017-11-24T17:06:54.048Z",
  "trackers": [],
  "app_name": "",
  "icon_hash": "133488413146636779444378132657184449536",
  "creator": "",
  "version_name": "0.15.8",
  "handle": "org.smssecure.smssecure"
},
...]
```
