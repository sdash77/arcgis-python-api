from __future__ import annotations

from requests.auth import AuthBase
from urllib.parse import parse_qs
from arcgis.auth._auth._schain import SupportMultiAuth

from arcgis.auth.tools._lazy import LazyLoader
from arcgis.auth.tools import parse_url

import re

HAS_SSPI = False
HAS_GSSAPI = False
HAS_KERBEROS = False
WINDOWS = False


try:
    # requests_kerberos = LazyLoader("requests_kerberos", strict=True)
    import requests_kerberos

    HAS_KERBEROS = True
except:
    HAS_KERBEROS = False


requests = LazyLoader("requests")

from ._utils import _split_username

__all__ = ["EsriKerberosAuth"]


###########################################################################
class EsriKerberosAuth(AuthBase, SupportMultiAuth):
    _token_url = None
    _server_log = None
    _tokens = None

    def __init__(
        self,
        referer: str | None = None,
        verify_cert: bool = True,
        *,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        """initializer"""
        if HAS_KERBEROS == False:
            raise ImportError(
                "requests_kerberos is required to use this authentication handler."
            )
        self.proxies = kwargs.pop("proxies", None)
        self.legacy = kwargs.pop("legacy", False)

        self._server_log = {}
        self._tokens = {}
        self._token_url = None
        self.verify_cert = verify_cert
        self._session: requests.Sesssion = kwargs.pop("session", requests.Session())
        mutual_auth_lu = {
            1: requests_kerberos.REQUIRED,
            2: requests_kerberos.OPTIONAL,
            3: requests_kerberos.DISABLED,
        }
        mutual_auth = mutual_auth_lu[kwargs.pop("mutual_authentication", 3)]
        if referer is None:
            self.referer = "http"
        else:
            self.referer = referer

        try:
            if username and password:
                uname_format = _split_username(username)
                prin = uname_format[0] + "@" + uname_format[1]
                self.auth = requests_kerberos.HTTPKerberosAuth(
                    mutual_authentication=mutual_auth,
                    principal=f"{prin}:{password}",
                    **kwargs,
                )
            else:
                self.auth = requests_kerberos.HTTPKerberosAuth(
                    mutual_authentication=mutual_auth, **kwargs
                )
        except ImportError:
            raise Exception(
                "Kerberos authentication requires `requests_kerberos` module."
            )

    # ----------------------------------------------------------------------
    def __str__(self):
        return f"<{self.__class__.__name__}>"

    # ----------------------------------------------------------------------
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    # ----------------------------------------------------------------------
    def generate_portal_server_token(self, r, **kwargs):
        """generates a server token using Portal token"""
        parsed = parse_url(r.url)
        if parsed.port:
            server_url = f'{parsed.scheme}://{parsed.netloc}:{parsed.port}/{parsed.path[1:].split("/")[0]}'
        else:
            server_url = (
                f'{parsed.scheme}://{parsed.netloc}/{parsed.path[1:].split("/")[0]}'
            )
        if (
            r.text.lower().find("invalid token") > -1
            or r.text.lower().find("token required") > -1
            or r.text.lower().find("token not found") > -1
        ) or server_url in self._server_log:
            expiration = 16000

            postdata = {
                "request": "getToken",
                "serverURL": server_url,
                "referer": self.referer or "http",
                "f": "json",
            }
            if expiration:
                postdata["expiration"] = expiration
            if server_url in self._server_log:
                token_url = self._server_log[server_url]
            else:
                info = self._session.get(
                    server_url + "/rest/info?f=json",
                    auth=self.auth,
                    verify=self.verify_cert,
                    proxies=self.proxies,
                ).json()
                token_url = info["authInfo"]["tokenServicesUrl"]
                self._server_log[server_url] = token_url
            if server_url in self._tokens:
                token_str = self._tokens[server_url]
            else:
                token = self._session.post(
                    token_url,
                    data=postdata,
                    auth=self.auth,
                    verify=self.verify_cert,
                    proxies=self.proxies,
                )
                token_str = token.json().get("token", None)
                if token_str is None:
                    return r
                self._tokens[server_url] = token_str
            # Recreate the request with the token
            #
            r.content
            r.raw.release_conn()
            r.request.headers["referer"] = self.referer or "http"
            r.request.headers["X-Esri-Authorization"] = f"Bearer {token_str}"

            if self.legacy and r.request.method == "GET":
                r.request.prepare_url(url=r.url, params={"token": token_str})
            elif self.legacy and r.request.method == "POST":
                data = parse_qs(r.body)
                data["token"] = token_str
                r.request.prepare_body(data, None, None)
            else:
                r.request.headers["X-Esri-Authorization"] = f"Bearer {token_str}"

            _r = r.connection.send(r.request, **kwargs)
            _r.headers["referer"] = self.referer or "http"
            _r.headers["X-Esri-Authorization"] = f"Bearer {token_str}"
            _r.history.append(r)
            if _r.status_code == 401:
                _r2 = self.auth.authenticate_user(_r)
                return _r2
            return _r
        return r

    # ----------------------------------------------------------------------
    @property
    def token(self) -> str:
        """
        Gets the token.  This is always `None` for `KerberosAuth`

        :returns: String
        """
        return None

    # ----------------------------------------------------------------------
    def __call__(self, r):
        self.auth.__call__(r)
        r.register_hook("response", self.generate_portal_server_token)
        return r
