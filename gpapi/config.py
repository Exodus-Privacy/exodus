from . import googleplay_pb2
from time import time
from os import path
from sys import version_info
from re import match

VERSION = version_info[0]
if VERSION == 2:
    import ConfigParser
else:
    import configparser


DFE_TARGETS = "CAEScFfqlIEG6gUYogFWrAISK1WDAg+hAZoCDgIU1gYEOIACFkLMAeQBnASLATlASUuyAyqCAjY5igOMBQzfA/IClwFbApUC4ANbtgKVAS7OAX8YswHFBhgDwAOPAmGEBt4OfKkB5weSB5AFASkiN68akgMaxAMSAQEBA9kBO7UBFE1KVwIDBGs3go6BBgEBAgMECQgJAQIEAQMEAQMBBQEBBAUEFQYCBgUEAwMBDwIBAgOrARwBEwMEAg0mrwESfTEcAQEKG4EBMxghChMBDwYGASI3hAEODEwXCVh/EREZA4sBYwEdFAgIIwkQcGQRDzQ2fTC2AjfVAQIBAYoBGRg2FhYFBwEqNzACJShzFFblAo0CFxpFNBzaAd0DHjIRI4sBJZcBPdwBCQGhAUd2A7kBLBVPngEECHl0UEUMtQETigHMAgUFCc0BBUUlTywdHDgBiAJ+vgKhAU0uAcYCAWQ/5ALUAw1UwQHUBpIBCdQDhgL4AY4CBQICjARbGFBGWzA1CAEMOQH+BRAOCAZywAIDyQZ2MgM3BxsoAgUEBwcHFia3AgcGTBwHBYwBAlcBggFxSGgIrAEEBw4QEqUCASsWadsHCgUCBQMD7QICA3tXCUw7ugJZAwGyAUwpIwM5AwkDBQMJA5sBCw8BNxBVVBwVKhebARkBAwsQEAgEAhESAgQJEBCZATMdzgEBBwG8AQQYKSMUkAEDAwY/CTs4/wEaAUt1AwEDAQUBAgIEAwYEDx1dB2wGeBFgTQ"
GOOGLE_PUBKEY = "AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pKRI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/6rmf5AAAAAwEAAQ=="
ACCOUNT = "HOSTED_OR_GOOGLE"

# parse phone config from the file 'device.properties'.
# if you want to add another phone, just create another section in
# the file. Some configurations for common phones can be found here:
# https://github.com/yeriomin/play-store-api/tree/master/src/main/resources
filepath = path.join(path.dirname(path.realpath(__file__)),
                     'device.properties')

if VERSION == 2:
    config = ConfigParser.ConfigParser()
else:
    config = configparser.ConfigParser()
config.read(filepath)


class InvalidLocaleError(Exception):
    pass

class InvalidTimezoneError(Exception):
    pass


def getDevicesCodenames():
    """Returns a list containing devices codenames"""
    return config.sections()


def getDevicesReadableNames():
    """Returns codename and readable name for each device"""
    return [{'codename': s,
             'readableName': config.get(s).get('userreadablename')}
            for s in getDevicesCodenames()]


class DeviceBuilder(object):

    def __init__(self, device):
        self.device = {}
        for (key, value) in config.items(device):
            self.device[key] = value

    def setLocale(self, locale):
        # test if provided locale is valid
        if locale is None or type(locale) is not str:
            raise InvalidLocaleError()

        # check if locale matches the structure of a common
        # value like "en_US"
        if match(r'[a-z]{2}\_[A-Z]{2}', locale) is None:
            raise InvalidLocaleError()
        self.locale = locale

    def setTimezone(self, timezone):
        if timezone is None or type(timezone) is not str:
            timezone = self.device.get('timezone')
            if timezone is None:
                raise InvalidTimezoneError()
        self.timezone = timezone

    def getBaseHeaders(self):
        return {"Accept-Language": self.locale.replace('_', '-'),
                "X-DFE-Encoded-Targets": DFE_TARGETS,
                "User-Agent": self.getUserAgent(),
                "X-DFE-Client-Id": "am-android-google",
                "X-DFE-MCCMNC": self.device.get('celloperator'),
                "X-DFE-Network-Type": "4",
                "X-DFE-Content-Filters": "",
                "X-DFE-Request-Params": "timeoutMs=4000"}

    def getDeviceUploadHeaders(self):
        headers = self.getBaseHeaders()
        headers["X-DFE-Enabled-Experiments"] = "cl:billing.select_add_instrument_by_default"
        headers["X-DFE-Unsupported-Experiments"] = ("nocache:billing.use_charging_poller,"
            "market_emails,buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,"
            "shekel_test,content_ratings,buyer_currency_in_app,nocache:encrypted_apk,recent_changes")
        headers["X-DFE-SmallestScreenWidthDp"] = "320"
        headers["X-DFE-Filter-Level"] = "3"
        return headers


    def getUserAgent(self):
        version_string = self.device.get('vending.versionstring')
        if version_string is None:
            version_string = '8.4.19.V-all [0] [FP] 175058788'
        return ("Android-Finsky/{versionString} ("
                "api=3"
                ",versionCode={versionCode}"
                ",sdk={sdk}"
                ",device={device}"
                ",hardware={hardware}"
                ",product={product}"
                ",platformVersionRelease={platform_v}"
                ",model={model}"
                ",buildId={build_id}"
                ",isWideScreen=0"
                ",supportedAbis={supported_abis}"
                ")").format(versionString=version_string,
                            versionCode=self.device.get('vending.version'),
                            sdk=self.device.get('build.version.sdk_int'),
                            device=self.device.get('build.device'),
                            hardware=self.device.get('build.hardware'),
                            product=self.device.get('build.product'),
                            platform_v=self.device.get('build.version.release'),
                            model=self.device.get('build.model'),
                            build_id=self.device.get('build.id'),
                            supported_abis=self.device.get('platforms').replace(',', ';'))

    def getAuthHeaders(self, gsfid):
        headers = {"User-Agent": ("GoogleAuth/1.4 ("
                                  "{device} {id}"
                                  ")").format(device=self.device.get('build.device'),
                                              id=self.device.get('build.id'))}
        if gsfid is not None:
            headers['device'] = "{0:x}".format(gsfid)
        return headers

    def getLoginParams(self, email, encrypted_passwd):
        return {"Email": email,
                "EncryptedPasswd": encrypted_passwd,
                "add_account": "1",
                "accountType": ACCOUNT,
                "google_play_services_version": self.device.get('gsf.version'),
                "has_permission": "1",
                "source": "android",
                "device_country": self.locale[0:2],
                "lang": self.locale,
                "client_sig": "38918a453d07199354f8b19af05ec6562ced5788",
                "callerSig": "38918a453d07199354f8b19af05ec6562ced5788",
                "droidguard_results": "dummy123"}

    def getAndroidCheckinRequest(self):
        request = googleplay_pb2.AndroidCheckinRequest()
        request.id = 0
        request.checkin.CopyFrom(self.getAndroidCheckin())
        request.locale = self.locale
        request.timeZone = self.timezone
        request.version = 3
        request.deviceConfiguration.CopyFrom(self.getDeviceConfig())
        request.fragment = 0
        return request

    def getDeviceConfig(self):
        libList = self.device['sharedlibraries'].split(",")
        featureList = self.device['features'].split(",")
        localeList = self.device['locales'].split(",")
        glList = self.device['gl.extensions'].split(",")
        platforms = self.device['platforms'].split(",")

        hasFiveWayNavigation = (self.device['hasfivewaynavigation'] == 'true')
        hasHardKeyboard = (self.device['hashardkeyboard'] == 'true')
        deviceConfig = googleplay_pb2.DeviceConfigurationProto()
        deviceConfig.touchScreen = int(self.device['touchscreen'])
        deviceConfig.keyboard = int(self.device['keyboard'])
        deviceConfig.navigation = int(self.device['navigation'])
        deviceConfig.screenLayout = int(self.device['screenlayout'])
        deviceConfig.hasHardKeyboard = hasHardKeyboard
        deviceConfig.hasFiveWayNavigation = hasFiveWayNavigation
        deviceConfig.screenDensity = int(self.device['screen.density'])
        deviceConfig.screenWidth = int(self.device['screen.width'])
        deviceConfig.screenHeight = int(self.device['screen.height'])
        deviceConfig.glEsVersion = int(self.device['gl.version'])
        for x in platforms:
            deviceConfig.nativePlatform.append(x)
        for x in libList:
            deviceConfig.systemSharedLibrary.append(x)
        for x in featureList:
            deviceConfig.systemAvailableFeature.append(x)
        for x in localeList:
            deviceConfig.systemSupportedLocale.append(x)
        for x in glList:
            deviceConfig.glExtension.append(x)
        return deviceConfig

    def getAndroidBuild(self):
        androidBuild = googleplay_pb2.AndroidBuildProto()
        androidBuild.id = self.device['build.fingerprint']
        androidBuild.product = self.device['build.hardware']
        androidBuild.carrier = self.device['build.brand']
        androidBuild.radio = self.device['build.radio']
        androidBuild.bootloader = self.device['build.bootloader']
        androidBuild.device = self.device['build.device']
        androidBuild.sdkVersion = int(self.device['build.version.sdk_int'])
        androidBuild.model = self.device['build.model']
        androidBuild.manufacturer = self.device['build.manufacturer']
        androidBuild.buildProduct = self.device['build.product']
        androidBuild.client = self.device['client']
        androidBuild.otaInstalled = False
        androidBuild.timestamp = int(time()/1000)
        androidBuild.googleServices = int(self.device['gsf.version'])
        return androidBuild

    def getAndroidCheckin(self):
        androidCheckin = googleplay_pb2.AndroidCheckinProto()
        androidCheckin.build.CopyFrom(self.getAndroidBuild())
        androidCheckin.lastCheckinMsec = 0
        androidCheckin.cellOperator = self.device['celloperator']
        androidCheckin.simOperator = self.device['simoperator']
        androidCheckin.roaming = self.device['roaming']
        androidCheckin.userNumber = 0
        return androidCheckin
