import platform
from requests.auth import AuthBase
from ._schain import SupportMultiAuth
from ..tools._lazy import LazyLoader
from ..tools import parse_url

if platform.platform().lower().find("windows") > -1:
    try:
        requests_negotiate_sspi = LazyLoader("requests_negotiate_sspi", strict=True)
        HAS_SSPI = True
    except:
        HAS_SSPI = False
else:
    HAS_SSPI = False

try:
    requests_gssapi = LazyLoader("requests_gssapi", strict=True)
    HAS_GSSAPI = True
except:
    HAS_GSSAPI = False

try:
    requests_kerberos = LazyLoader("requests_kerberos", strict=True)
    HAS_KERBEROS = True
except:
    HAS_KERBEROS = False

requests_ntlm = LazyLoader("requests_ntlm", strict=True)
requests = LazyLoader("requests")


class EsriWindowsAuth(AuthBase, SupportMultiAuth):

    _token_url = None
    _server_log = None
    _tokens = None

    def __init__(self, username=None, password=None, referer=None, verify_cert=True):
        self._server_log = {}
        self._tokens = {}
        self._token_url = None
        self.verify_cert = verify_cert
        if referer is None:
            self.referer = "http"
        else:
            self.referer = referer

        try:
            if not username and not password and HAS_SSPI:
                self.auth = requests_negotiate_sspi.HttpNegotiateAuth()
            elif not username and not password and HAS_GSSAPI:
                self.auth = requests_gssapi.HTTPSPNEGOAuth()
            elif username and password:
                self.auth = requests_ntlm.HttpNtlmAuth(username, password)
            else:
                raise ValueError("")
        except ImportError:
            raise Exception(
                "NTLM authentication requires requests_negotiate_sspi module."
            )

    def generate_portal_server_token(self, r, **kwargs):
        """generates a server token using Portal token"""
        parsed = parse_url(r.url)
        if (
            r.text.lower().find("invalid token") > -1
            or r.text.lower().find("token required") > -1
        ) or parsed.netloc in self._server_log:
            expiration = 16000
            if parsed.port:
                server_url = f'{parsed.scheme}://{parsed.netloc}:{parsed.port}/{parsed.path[1:].split("/")[0]}'
            else:
                server_url = (
                    f'{parsed.scheme}://{parsed.netloc}/{parsed.path[1:].split("/")[0]}'
                )
            postdata = {
                "request": "getToken",
                "serverURL": server_url,
                "referer": self.referer or "http",
                "f": "json",
            }
            if expiration:
                postdata["expiration"] = expiration
            if parsed.netloc in self._server_log:
                token_url = self._server_log[parsed.netloc]
            else:
                info = requests.get(
                    server_url + "/rest/info?f=json",
                    auth=self.auth,
                    verify=self.verify_cert,
                ).json()
                token_url = info["authInfo"]["tokenServicesUrl"]
                self._server_log[parsed.netloc] = token_url
            if server_url in self._tokens:
                token_str = self._tokens[server_url]
            else:
                token = requests.post(token_url, data=postdata, auth=self.auth)
                token_str = token.json().get("token", None)
                if token_str is None:
                    return r
                self._tokens[server_url] = token_str
            # Recreate the request with the token
            #
            r.content
            r.raw.release_conn()
            r.request.headers["Referer"] = self.referer or "http"
            r.request.headers["X-Esri-Authorization"] = f"Bearer {token_str}"
            _r = r.connection.send(r.request, **kwargs)
            _r.headers["Referer"] = self.referer or "http"
            _r.headers["X-Esri-Authorization"] = f"Bearer {token_str}"
            _r.history.append(r)
            return _r
        return r

    # ----------------------------------------------------------------------
    def __call__(self, r):
        self.auth.__call__(r)
        r.register_hook("response", self.generate_portal_server_token)
        return r


class EsriKerberosAuth(AuthBase, SupportMultiAuth):

    _token_url = None
    _server_log = None
    _tokens = None

    def __init__(self, referer=None, verify_cert=True):
        """initializer"""
        if HAS_KERBEROS == False:
            raise ImportError(
                "requests_kerberos is required to use this authentication handler."
            )
        self._server_log = {}
        self._tokens = {}
        self._token_url = None
        self.verify_cert = verify_cert
        if referer is None:
            self.referer = "http"
        else:
            self.referer = referer

        try:
            import requests_kerberos

            self.auth = requests_kerberos.HTTPKerberosAuth(
                mutual_authentication=requests_kerberos.OPTIONAL
            )
        except ImportError:
            raise Exception(
                "Kerberos authentication requires `requests_kerberos` module."
            )

    def generate_portal_server_token(self, r, **kwargs):
        """generates a server token using Portal token"""
        parsed = parse_url(r.url)
        if (
            r.text.lower().find("invalid token") > -1
            or r.text.lower().find("token required") > -1
        ) or parsed.netloc in self._server_log:
            expiration = 16000
            if parsed.port:
                server_url = f'{parsed.scheme}://{parsed.netloc}:{parsed.port}/{parsed.path[1:].split("/")[0]}'
            else:
                server_url = (
                    f'{parsed.scheme}://{parsed.netloc}/{parsed.path[1:].split("/")[0]}'
                )
            postdata = {
                "request": "getToken",
                "serverURL": server_url,
                "referer": self.referer or "http",
                "f": "json",
            }
            if expiration:
                postdata["expiration"] = expiration
            if parsed.netloc in self._server_log:
                token_url = self._server_log[parsed.netloc]
            else:
                info = requests.get(
                    server_url + "/rest/info?f=json",
                    auth=self.auth,
                    verify=self.verify_cert,
                ).json()
                token_url = info["authInfo"]["tokenServicesUrl"]
                self._server_log[parsed.netloc] = token_url
            if server_url in self._tokens:
                token_str = self._tokens[server_url]
            else:
                token = requests.post(token_url, data=postdata, auth=self.auth)
                token_str = token.json().get("token", None)
                if token_str is None:
                    return r
                self._tokens[server_url] = token_str
            # Recreate the request with the token
            #
            r.content
            r.raw.release_conn()
            r.request.headers["Referer"] = self.referer or "http"
            r.request.headers["X-Esri-Authorization"] = f"Bearer {token_str}"
            _r = r.connection.send(r.request, **kwargs)
            _r.headers["Referer"] = self.referer or "http"
            _r.headers["X-Esri-Authorization"] = f"Bearer {token_str}"
            _r.history.append(r)
            return _r
        return r

    # ----------------------------------------------------------------------
    def __call__(self, r):
        self.auth.__call__(r)
        r.register_hook("response", self.generate_portal_server_token)
        return r
