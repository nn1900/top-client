import hashlib
import http.client
import json

from urllib.parse import urlparse
from urllib.parse import urlencode
from datetime import datetime


class TopClient:
    """
    Taobao Open API Client
    """

    def __init__(self, appkey, secret,
                 url="http://gw.api.taobao.com/router/rest",
                 session=None,
                 subway_token=None,
                 debug=False
                 ):
        """
        Create an instance of TopClient

        :param appkey: app key obtained from taobao open platform
        :param secret: app secret obtained from taobao open platform
        :param url: taobao open api end point (server url)
        :param session: default session used for api requests
        :param subway_token: default subway token used for api requests
        :param debug: true to output debug information
        """
        self.appkey = appkey
        self.secret = secret
        self.url = url
        self.session = session
        self.subway_token = subway_token
        self.debug = debug

    def sign(self, params):
        keys = sorted(params.keys())
        s = "%s%s%s" % (
            self.secret,
            "".join("%s%s" % (key, params[key]) for key in keys
                    if params[key] is not None),
            self.secret
        )
        data = s.encode('utf-8')
        digest = hashlib.md5(data).hexdigest().upper()
        return digest

    def request(self,
                apiname=None,
                params=None,
                session=None,
                format="json",
                method="get",
                version="2.0",
                timestamp=None,
                timeout=30
                ):
        """
        Make a taobao open API request
        :param apiname: name of the api to request
        :param params: api specific params
        :param session: request specific session key
        :param format: response format (json|xml)
        :param method: request method (get|post)
        :param version: api version (default to 2.0)
        :param timestamp: timestamp used only for debug purpose
        :param timeout: request timeout default to 30s
        :return: API response if the request is success
        :raises RequestException: network related exception
        :raises TopException: API related exception
        """
        if params is None:
            raise Exception("params is required")

        api_specific_params = params
        common_params = {
            "app_key": self.appkey,
            "method": apiname,
            "v": version,
            "format": format,
            "sign_method": "md5",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "partner_id": "taobao-sdk-python-20170425"
        }

        params = api_specific_params.copy()
        params.update(common_params)

        if session is not None:
            params['session'] = session

        if timestamp is not None:
            params['timestamp'] = timestamp

        if 'session' not in params and self.session is not None:
            params['session'] = self.session

        if 'subway_token' not in params and self.subway_token is not None:
            params['subway_token'] = self.subway_token

        sign = self.sign(params)

        method = method.upper()

        url = self.url
        body = None
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive"
        }

        (host, port) = urlparse(url).netloc.split(':') + [80]

        if method == "GET":
            params['sign'] = sign
            url = url + '?' + urlencode(params)
            if self.debug:
                print(url)
        else:
            del api_specific_params['session']
            body = urlencode(api_specific_params)
            headers['Content-Type'] = \
                "application/x-www-form-urlencoded; charset=utf-8"

        if self.debug:
            print(
                "url: %s\nbody: %s\nhash: %s" % (
                    url, body or "<none>", sign)
            )

        conn = http.client.HTTPConnection(host, int(port), timeout=timeout)
        conn.connect()
        conn.request(method, url, body=body, headers=headers)
        response = conn.getresponse()
        result = response.read()

        if self.debug:
            print("status: %s\nresponse text: %s" % (response.status, result))

        conn.close()

        if response.status is not 200:
            raise RequestException("Error sending request: %s" % result)

        resultobj = json.loads(result)

        if "error_response" in resultobj:
            errorobj = resultobj["error_response"]
            exception = TopException(
                errorcode=errorobj.get("code", None),
                message=errorobj.get("msg", None),
                subcode=errorobj.get("sub_code", None),
                submsg=errorobj.get("sub_msg", None),
                application_host=response.getheader("Application-Host", ""),
                service_host=response.getheader("Location-Host", "")
            )
            raise exception

        response_prop_name = apiname[7:].replace(".", "_") + "_response"

        return resultobj[response_prop_name]

    # -----------------------------------------------------------------
    # The following methods implement convenient API specific requests
    # -----------------------------------------------------------------

    def get_adgroup_base_rpt(self, **kwargs):
        """
        Get adgroup keyword base reports
        :param kwargs: api params
        :return: base report list
        """
        res = self.request("taobao.simba.rpt.adgroupkeywordbase.get", kwargs)
        return res.get("rpt_adgroupkeyword_base_list", None)

    def get_adgroup_effect_rpt(self, **kwargs):
        """
        Get adgroup keyword effect reports
        :param kwargs: api params
        :return: effect report list
        """
        res = self.request("taobao.simba.rpt.adgroupkeywordeffect.get", kwargs)
        return res.get("rpt_adgroupkeyword_effect_list", None)

    # TODO: add more api methods


class RequestException(Exception):
    """
    Request exception
    """
    pass


class TopException(Exception):
    """
    Taobao Open API exception
    """
    def __init__(self,
                 errorcode=None,
                 message=None,
                 subcode=None,
                 submsg=None,
                 application_host=None,
                 service_host=None
                 ):
        self.errorcode = errorcode
        self.message = message
        self.subcode = subcode
        self.submsg = submsg
        self.application_host = application_host
        self.service_host = service_host

    def __str__(self):
        return "errorcode=%s, message=%s, subcode=%s, submsg=%s" % \
               (self.errorcode, self.message, self.subcode, self.submsg)
