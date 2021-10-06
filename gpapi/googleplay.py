#!/usr/bin/python

from base64 import b64decode, urlsafe_b64encode
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.asymmetric import padding

import requests
import ssl

from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_

from . import googleplay_pb2, config, utils

ssl_verify = True

BASE = "https://android.clients.google.com/"
FDFE = BASE + "fdfe/"
CHECKIN_URL = BASE + "checkin"
AUTH_URL = BASE + "auth"

UPLOAD_URL = FDFE + "uploadDeviceConfig"
SEARCH_URL = FDFE + "search"
DETAILS_URL = FDFE + "details"
HOME_URL = FDFE + "homeV2"
BROWSE_URL = FDFE + "browse"
DELIVERY_URL = FDFE + "delivery"
PURCHASE_URL = FDFE + "purchase"
SEARCH_SUGGEST_URL = FDFE + "searchSuggest"
BULK_URL = FDFE + "bulkDetails"
LOG_URL = FDFE + "log"
TOC_URL = FDFE + "toc"
ACCEPT_TOS_URL = FDFE + "acceptTos"
LIST_URL = FDFE + "list"
REVIEWS_URL = FDFE + "rev"

CONTENT_TYPE_URLENC = "application/x-www-form-urlencoded; charset=UTF-8"
CONTENT_TYPE_PROTO = "application/x-protobuf"


class SSLContext(ssl.SSLContext):
    def set_alpn_protocols(self, protocols):
        """
        ALPN headers cause Google to return 403 Bad Authentication.
        """
        pass


class AuthHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        """
        Secure settings from ssl.create_default_context(), but without
        ssl.OP_NO_TICKET which causes Google to return 403 Bad
        Authentication.
        """
        context = SSLContext()
        context.set_ciphers(ssl_.DEFAULT_CIPHERS)
        context.verify_mode = ssl.CERT_REQUIRED
        context.options &= ~ssl_.OP_NO_TICKET
        self.poolmanager = PoolManager(*args, ssl_context=context, **kwargs)


class LoginError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RequestError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SecurityCheckError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GooglePlayAPI(object):
    """Google Play Unofficial API Class

    Usual APIs methods are login(), search(), details(), bulkDetails(),
    download(), browse(), reviews() and list()."""

    def __init__(self, locale="en_US", timezone="UTC", device_codename="bacon",
                 proxies_config=None):
        self.authSubToken = None
        self.gsfId = None
        self.device_config_token = None
        self.deviceCheckinConsistencyToken = None
        self.dfeCookie = None
        self.proxies_config = proxies_config
        self.deviceBuilder = config.DeviceBuilder(device_codename)
        self.setLocale(locale)
        self.setTimezone(timezone)
        self.session = requests.session()
        self.session.mount('https://', AuthHTTPAdapter())

    def setLocale(self, locale):
        self.deviceBuilder.setLocale(locale)

    def setTimezone(self, timezone):
        self.deviceBuilder.setTimezone(timezone)

    def encryptPassword(self, login, passwd):
        """Encrypt credentials using the google publickey, with the
        RSA algorithm"""

        # structure of the binary key:
        #
        # *-------------------------------------------------------*
        # | modulus_length | modulus | exponent_length | exponent |
        # *-------------------------------------------------------*
        #
        # modulus_length and exponent_length are uint32
        binaryKey = b64decode(config.GOOGLE_PUBKEY)
        # modulus
        i = utils.readInt(binaryKey, 0)
        modulus = utils.toBigInt(binaryKey[4:][0:i])
        # exponent
        j = utils.readInt(binaryKey, i + 4)
        exponent = utils.toBigInt(binaryKey[i + 8:][0:j])

        # calculate SHA1 of the pub key
        digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
        digest.update(binaryKey)
        h = b'\x00' + digest.finalize()[0:4]

        # generate a public key
        der_data = encode_dss_signature(modulus, exponent)
        publicKey = load_der_public_key(der_data, backend=default_backend())

        # encrypt email and password using pubkey
        to_be_encrypted = login.encode() + b'\x00' + passwd.encode()
        ciphertext = publicKey.encrypt(
            to_be_encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )

        return urlsafe_b64encode(h + ciphertext)

    def setAuthSubToken(self, authSubToken):
        self.authSubToken = authSubToken

    def getHeaders(self, upload_fields=False):
        """Return the default set of request headers, which
        can later be expanded, based on the request type"""

        if upload_fields:
            headers = self.deviceBuilder.getDeviceUploadHeaders()
        else:
            headers = self.deviceBuilder.getBaseHeaders()
        if self.gsfId is not None:
            headers["X-DFE-Device-Id"] = "{0:x}".format(self.gsfId)
        if self.authSubToken is not None:
            headers["Authorization"] = "GoogleLogin auth=%s" % self.authSubToken
        if self.device_config_token is not None:
            headers["X-DFE-Device-Config-Token"] = self.device_config_token
        if self.deviceCheckinConsistencyToken is not None:
            headers["X-DFE-Device-Checkin-Consistency-Token"] = self.deviceCheckinConsistencyToken
        if self.dfeCookie is not None:
            headers["X-DFE-Cookie"] = self.dfeCookie
        return headers

    def checkin(self, email, ac2dmToken):
        headers = self.getHeaders()
        headers["Content-Type"] = CONTENT_TYPE_PROTO

        request = self.deviceBuilder.getAndroidCheckinRequest()

        stringRequest = request.SerializeToString()
        res = self.session.post(CHECKIN_URL, data=stringRequest,
                                headers=headers, verify=ssl_verify,
                                proxies=self.proxies_config)
        response = googleplay_pb2.AndroidCheckinResponse()
        response.ParseFromString(res.content)
        self.deviceCheckinConsistencyToken = response.deviceCheckinConsistencyToken

        # checkin again to upload gfsid
        request.id = response.androidId
        request.securityToken = response.securityToken
        request.accountCookie.append("[" + email + "]")
        request.accountCookie.append(ac2dmToken)
        stringRequest = request.SerializeToString()
        self.session.post(CHECKIN_URL,
                          data=stringRequest,
                          headers=headers,
                          verify=ssl_verify,
                          proxies=self.proxies_config)

        return response.androidId

    def uploadDeviceConfig(self):
        """Upload the device configuration of the fake device
        selected in the __init__ methodi to the google account."""

        upload = googleplay_pb2.UploadDeviceConfigRequest()
        upload.deviceConfiguration.CopyFrom(self.deviceBuilder.getDeviceConfig())
        headers = self.getHeaders(upload_fields=True)
        stringRequest = upload.SerializeToString()
        response = self.session.post(UPLOAD_URL, data=stringRequest,
                                     headers=headers,
                                     verify=ssl_verify,
                                     timeout=60,
                                     proxies=self.proxies_config)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        try:
            if response.payload.HasField('uploadDeviceConfigResponse'):
                self.device_config_token = response.payload.uploadDeviceConfigResponse
                self.device_config_token = self.device_config_token.uploadDeviceConfigToken
        except ValueError:
            pass

    def login(self, email=None, password=None, gsfId=None, authSubToken=None):
        """Login to your Google Account.
        For first time login you should provide:
            * email
            * password
        For the following logins you need to provide:
            * gsfId
            * authSubToken"""
        if email is not None and password is not None:
            # First time setup, where we obtain an ac2dm token and
            # upload device information

            encryptedPass = self.encryptPassword(email, password).decode('utf-8')
            # AC2DM token
            params = self.deviceBuilder.getLoginParams(email, encryptedPass)
            params['service'] = 'ac2dm'
            params['add_account'] = '1'
            params['callerPkg'] = 'com.google.android.gms'
            headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
            headers['app'] = 'com.google.android.gsm'
            response = self.session.post(AUTH_URL, data=params, verify=ssl_verify,
                                         proxies=self.proxies_config)
            data = response.text.split()
            params = {}
            for d in data:
                if "=" not in d:
                    continue
                k, v = d.split("=", 1)
                params[k.strip().lower()] = v.strip()
            if "auth" in params:
                ac2dmToken = params["auth"]
            elif "error" in params:
                if "NeedsBrowser" in params["error"]:
                    raise SecurityCheckError("Security check is needed, try to visit "
                                             "https://accounts.google.com/b/0/DisplayUnlockCaptcha "
                                             "to unlock, or setup an app-specific password")
                raise LoginError("server says: " + params["error"])
            else:
                raise LoginError("Auth token not found.")

            self.gsfId = self.checkin(email, ac2dmToken)
            self.getAuthSubToken(email, encryptedPass)
            self.uploadDeviceConfig()
        elif gsfId is not None and authSubToken is not None:
            # no need to initialize API
            self.gsfId = gsfId
            self.setAuthSubToken(authSubToken)
            # check if token is valid with a simple search
            self.search('drv')
        else:
            raise LoginError('Either (email,pass) or (gsfId, authSubToken) is needed')

    def getAuthSubToken(self, email, passwd):
        requestParams = self.deviceBuilder.getLoginParams(email, passwd)
        requestParams['service'] = 'androidmarket'
        requestParams['app'] = 'com.android.vending'
        headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
        headers['app'] = 'com.android.vending'
        response = self.session.post(AUTH_URL,
                                     data=requestParams,
                                     verify=ssl_verify,
                                     headers=headers,
                                     proxies=self.proxies_config)
        data = response.text.split()
        params = {}
        for d in data:
            if "=" not in d:
                continue
            k, v = d.split("=", 1)
            params[k.strip().lower()] = v.strip()
        if "token" in params:
            master_token = params["token"]
            second_round_token = self.getSecondRoundToken(master_token, requestParams)
            self.setAuthSubToken(second_round_token)
        elif "error" in params:
            raise LoginError("server says: " + params["error"])
        else:
            raise LoginError("auth token not found.")

    def getSecondRoundToken(self, first_token, params):
        if self.gsfId is not None:
            params['androidId'] = "{0:x}".format(self.gsfId)
        params['Token'] = first_token
        params['check_email'] = '1'
        params['token_request_options'] = 'CAA4AQ=='
        params['system_partition'] = '1'
        params['_opt_is_called_from_account_manager'] = '1'
        params.pop('Email')
        params.pop('EncryptedPasswd')
        headers = self.deviceBuilder.getAuthHeaders(self.gsfId)
        headers['app'] = 'com.android.vending'
        response = self.session.post(AUTH_URL,
                                     data=params,
                                     headers=headers,
                                     verify=ssl_verify,
                                     proxies=self.proxies_config)
        data = response.text.split()
        params = {}
        for d in data:
            if "=" not in d:
                continue
            k, v = d.split("=", 1)
            params[k.strip().lower()] = v.strip()
        if "auth" in params:
            return params["auth"]
        elif "error" in params:
            raise LoginError("server says: " + params["error"])
        else:
            raise LoginError("Auth token not found.")

    def executeRequestApi2(self, path, post_data=None, content_type=CONTENT_TYPE_URLENC, params=None):
        if self.authSubToken is None:
            raise LoginError("You need to login before executing any request")
        headers = self.getHeaders()
        headers["Content-Type"] = content_type

        if post_data is not None:
            response = self.session.post(path,
                                         data=str(post_data),
                                         headers=headers,
                                         params=params,
                                         verify=ssl_verify,
                                         timeout=60,
                                         proxies=self.proxies_config)
        else:
            response = self.session.get(path,
                                        headers=headers,
                                        params=params,
                                        verify=ssl_verify,
                                        timeout=60,
                                        proxies=self.proxies_config)

        message = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if message.commands.displayErrorMessage != "":
            raise RequestError(message.commands.displayErrorMessage)

        return message

    def searchSuggest(self, query):
        params = {"c": "3",
                  "q": requests.utils.quote(query),
                  "ssis": "120",
                  "sst": "2"}
        data = self.executeRequestApi2(SEARCH_SUGGEST_URL, params=params)
        entryIterator = data.payload.searchSuggestResponse.entry
        return list(map(utils.parseProtobufObj, entryIterator))

    def search(self, query):
        """ Search the play store for an app.

        nb_result (int): is the maximum number of result to be returned

        offset (int): is used to take result starting from an index.
        """
        if self.authSubToken is None:
            raise LoginError("You need to login before executing any request")

        path = SEARCH_URL + "?c=3&q={}".format(requests.utils.quote(query))
        # FIXME: not sure if this toc call should be here
        self.toc()
        data = self.executeRequestApi2(path)
        if utils.hasPrefetch(data):
            response = data.preFetch[0].response
        else:
            response = data
        resIterator = response.payload.listResponse.doc
        return list(map(utils.parseProtobufObj, resIterator))

    def details(self, packageName):
        """Get app details from a package name.

        packageName is the app unique ID (usually starting with 'com.')."""
        path = DETAILS_URL + "?doc={}".format(requests.utils.quote(packageName))
        data = self.executeRequestApi2(path)
        return utils.parseProtobufObj(data.payload.detailsResponse.docV2)

    def bulkDetails(self, packageNames):
        """Get several apps details from a list of package names.

        This is much more efficient than calling N times details() since it
        requires only one request. If an item is not found it returns an empty object
        instead of throwing a RequestError('Item not found') like the details() function

        Args:
            packageNames (list): a list of app IDs (usually starting with 'com.').

        Returns:
            a list of dictionaries containing docv2 data, or None
            if the app doesn't exist"""

        params = {'au': '1'}
        req = googleplay_pb2.BulkDetailsRequest()
        req.docid.extend(packageNames)
        data = req.SerializeToString()
        message = self.executeRequestApi2(BULK_URL,
                                          post_data=data.decode("utf-8"),
                                          content_type=CONTENT_TYPE_PROTO,
                                          params=params)
        response = message.payload.bulkDetailsResponse
        return [None if not utils.hasDoc(entry) else
                utils.parseProtobufObj(entry.doc)
                for entry in response.entry]

    def home(self, cat=None):
        path = HOME_URL + "?c=3&nocache_isui=true"
        if cat is not None:
            path += "&cat={}".format(cat)
        data = self.executeRequestApi2(path)
        if utils.hasPrefetch(data):
            response = data.preFetch[0].response
        else:
            response = data
        resIterator = response.payload.listResponse.doc
        return list(map(utils.parseProtobufObj, resIterator))

    def browse(self, cat=None, subCat=None):
        """Browse categories. If neither cat nor subcat are specified,
        return a list of categories, otherwise it return a list of apps
        using cat (category ID) and subCat (subcategory ID) as filters."""
        path = BROWSE_URL + "?c=3"
        if cat is not None:
            path += "&cat={}".format(requests.utils.quote(cat))
        if subCat is not None:
            path += "&ctr={}".format(requests.utils.quote(subCat))
        data = self.executeRequestApi2(path)

        return utils.parseProtobufObj(data.payload.browseResponse)

    def list(self, cat, ctr=None, nb_results=None, offset=None):
        """List all possible subcategories for a specific category. If
        also a subcategory is provided, list apps from this category.

        Args:
            cat (str): category id
            ctr (str): subcategory id
            nb_results (int): if a subcategory is specified, limit number
                of results to this number
            offset (int): if a subcategory is specified, start counting from this
                result
        Returns:
            A list of categories. If subcategory is specified, a list of apps in this
            category.
        """
        path = LIST_URL + "?c=3&cat={}".format(requests.utils.quote(cat))
        if ctr is not None:
            path += "&ctr={}".format(requests.utils.quote(ctr))
        if nb_results is not None:
            path += "&n={}".format(requests.utils.quote(str(nb_results)))
        if offset is not None:
            path += "&o={}".format(requests.utils.quote(str(offset)))
        data = self.executeRequestApi2(path)
        clusters = []
        docs = []
        if ctr is None:
            # list subcategories
            for pf in data.preFetch:
                for cluster in pf.response.payload.listResponse.doc:
                    clusters.extend(cluster.child)
            return [c.docid for c in clusters]
        else:
            apps = []
            for d in data.payload.listResponse.doc:  # categories
                for c in d.child:  # sub-category
                    for a in c.child:  # app
                        apps.append(utils.parseProtobufObj(a))
            return apps

    def reviews(self, packageName, filterByDevice=False, sort=2,
                nb_results=None, offset=None):
        """Browse reviews for an application

        Args:
            packageName (str): app unique ID.
            filterByDevice (bool): filter results for current device
            sort (int): sorting criteria (values are unknown)
            nb_results (int): max number of reviews to return
            offset (int): return reviews starting from an offset value

        Returns:
            dict object containing all the protobuf data returned from
            the api
        """
        # TODO: select the number of reviews to return
        path = REVIEWS_URL + "?doc={}&sort={}".format(requests.utils.quote(packageName), sort)
        if nb_results is not None:
            path += "&n={}".format(nb_results)
        if offset is not None:
            path += "&o={}".format(offset)
        if filterByDevice:
            path += "&dfil=1"
        data = self.executeRequestApi2(path)
        output = []
        for review in data.payload.reviewResponse.getResponse.review:
            output.append(utils.parseProtobufObj(review))
        return output

    def _deliver_data(self, url, cookies):
        headers = self.getHeaders()
        response = self.session.get(url, headers=headers,
                                    cookies=cookies, verify=ssl_verify,
                                    stream=True, timeout=60,
                                    proxies=self.proxies_config)
        total_size = response.headers.get('content-length')
        chunk_size = 32 * (1 << 10)
        return {'data': response.iter_content(chunk_size=chunk_size),
                'total_size': total_size,
                'chunk_size': chunk_size}

    def delivery(self, packageName, versionCode=None, offerType=1,
                 downloadToken=None, expansion_files=False):
        """Download an already purchased app.

        Args:
            packageName (str): app unique ID (usually starting with 'com.')
            versionCode (int): version to download
            offerType (int): different type of downloads (mostly unused for apks)
            downloadToken (str): download token returned by 'purchase' API
            progress_bar (bool): wether or not to print a progress bar to stdout

        Returns:
            Dictionary containing apk data and a list of expansion files. As stated
            in android documentation, there can be at most 2 expansion files, one with
            main content, and one for patching the main content. Their names should
            follow this format:

            [main|patch].<expansion-version>.<package-name>.obb

            Data to build this name string is provided in the dict object. For more
            info check https://developer.android.com/google/play/expansion-files.html
        """

        if versionCode is None:
            # pick up latest version
            appDetails = self.details(packageName).get('details').get('appDetails')
            versionCode = appDetails.get('versionCode')

        params = {'ot': str(offerType),
                  'doc': packageName,
                  'vc': str(versionCode)}
        headers = self.getHeaders()
        if downloadToken is not None:
            params['dtok'] = downloadToken
        response = self.session.get(DELIVERY_URL, headers=headers,
                                    params=params, verify=ssl_verify,
                                    timeout=60,
                                    proxies=self.proxies_config)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)
        elif response.payload.deliveryResponse.appDeliveryData.downloadUrl == "":
            raise RequestError('App not purchased')
        else:
            result = {}
            result['docId'] = packageName
            result['additionalData'] = []
            result['splits'] = []
            downloadUrl = response.payload.deliveryResponse.appDeliveryData.downloadUrl
            cookie = response.payload.deliveryResponse.appDeliveryData.downloadAuthCookie[0]
            cookies = {
                str(cookie.name): str(cookie.value)
            }
            result['file'] = self._deliver_data(downloadUrl, cookies)

            for split in response.payload.deliveryResponse.appDeliveryData.split:
                a = {}
                a['name'] = split.name
                a['file'] = self._deliver_data(split.downloadUrl, None)
                result['splits'].append(a)

            if not expansion_files:
                return result
            for obb in response.payload.deliveryResponse.appDeliveryData.additionalFile:
                a = {}
                # fileType == 0 -> main
                # fileType == 1 -> patch
                if obb.fileType == 0:
                    obbType = 'main'
                else:
                    obbType = 'patch'
                a['type'] = obbType
                a['versionCode'] = obb.versionCode
                a['file'] = self._deliver_data(obb.downloadUrl, None)
                result['additionalData'].append(a)
            return result

    def download(self, packageName, versionCode=None, offerType=1, expansion_files=False):
        """Download an app and return its raw data (APK file). Free apps need
        to be "purchased" first, in order to retrieve the download cookie.
        If you want to download an already purchased app, use *delivery* method.

        Args:
            packageName (str): app unique ID (usually starting with 'com.')
            versionCode (int): version to download
            offerType (int): different type of downloads (mostly unused for apks)
            downloadToken (str): download token returned by 'purchase' API
            progress_bar (bool): wether or not to print a progress bar to stdout

        Returns
            Dictionary containing apk data and optional expansion files
            (see *delivery*)
        """

        if self.authSubToken is None:
            raise LoginError("You need to login before executing any request")

        if versionCode is None:
            # pick up latest version
            appDetails = self.details(packageName).get('details').get('appDetails')
            versionCode = appDetails.get('versionCode')

        headers = self.getHeaders()
        params = {'ot': str(offerType),
                  'doc': packageName,
                  'vc': str(versionCode)}
        response = self.session.post(PURCHASE_URL, headers=headers,
                                     params=params, verify=ssl_verify,
                                     timeout=60,
                                     proxies=self.proxies_config)

        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)
        else:
            dlToken = response.payload.buyResponse.downloadToken
            return self.delivery(packageName, versionCode, offerType, dlToken,
                                 expansion_files=expansion_files)

    def log(self, docid):
        log_request = googleplay_pb2.LogRequest()
        log_request.downloadConfirmationQuery = "confirmFreeDownload?doc=" + docid
        timestamp = int(datetime.now().timestamp())
        log_request.timestamp = timestamp

        string_request = log_request.SerializeToString()
        response = self.session.post(LOG_URL,
                                     data=string_request,
                                     headers=self.getHeaders(),
                                     verify=ssl_verify,
                                     timeout=60,
                                     proxies=self.proxies_config)
        response = googleplay_pb2.ResponseWrapper.FromString(response.content)
        if response.commands.displayErrorMessage != "":
            raise RequestError(response.commands.displayErrorMessage)

    def toc(self):
        response = self.session.get(TOC_URL,
                                    headers=self.getHeaders(),
                                    verify=ssl_verify,
                                    timeout=60,
                                    proxies=self.proxies_config)
        data = googleplay_pb2.ResponseWrapper.FromString(response.content)
        tocResponse = data.payload.tocResponse
        if utils.hasTosContent(tocResponse) and utils.hasTosToken(tocResponse):
            self.acceptTos(tocResponse.tosToken)
        if utils.hasCookie(tocResponse):
            self.dfeCookie = tocResponse.cookie
        return utils.parseProtobufObj(tocResponse)

    def acceptTos(self, tosToken):
        params = {
            "tost": tosToken,
            "toscme": "false"
        }
        response = self.session.get(ACCEPT_TOS_URL,
                                    headers=self.getHeaders(),
                                    params=params,
                                    verify=ssl_verify,
                                    timeout=60,
                                    proxies=self.proxies_config)
        data = googleplay_pb2.ResponseWrapper.FromString(response.content)
        return utils.parseProtobufObj(data.payload.acceptTosResponse)

    @staticmethod
    def getDevicesCodenames():
        return config.getDevicesCodenames()

    @staticmethod
    def getDevicesReadableNames():
        return config.getDevicesReadableNames()
