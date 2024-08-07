from __future__ import annotations
import os
import ssl
import tempfile

import datetime as _dt
import requests
import truststore
import cryptography

try:
    from ssl import PROTOCOL_TLS_CLIENT as default_ssl_protocol
except ImportError:
    from ssl import PROTOCOL_SSLv23 as default_ssl_protocol
from requests.adapters import HTTPAdapter
from .certificate import _handle_cert_context

from requests.utils import (
    DEFAULT_CA_BUNDLE_PATH,
    extract_zipped_paths,
    get_auth_from_url,
    get_encoding_from_headers,
    prepend_scheme_if_needed,
    select_proxy,
    urldefragauth,
)
from requests.adapters import (
    HTTPAdapter,
    DEFAULT_POOLSIZE,
    DEFAULT_RETRIES,
    DEFAULT_POOLBLOCK,
)
from requests.compat import basestring, urlparse

__all__ = ["PKIAdapter", "TruststoreAdapter", "EsriHostHeaderSSLAdapter"]


###########################################################################
class PKIAdapter(requests.adapters.HTTPAdapter):
    # ---------------------------------------------------------------------
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} >"

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"< {self.__class__.__name__} >"

    # ---------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        pki_data = kwargs.pop("pki_data", None)

        password = kwargs.pop("pki_password", None)
        ssl_protocol_or_none = kwargs.pop("ssl_protocol", None)
        if pki_data is None:
            raise ValueError('"pki_data" is missing')

        if password is None:
            password_bytes = None
        elif isinstance(password, bytes):
            password_bytes = password
        elif isinstance(password, str):
            password_bytes = password.encode("utf8")
        else:
            raise TypeError("Password must be a None, string or bytes.")
        if ssl_protocol_or_none is None:
            ssl_protocol = default_ssl_protocol
        else:
            ssl_protocol = ssl_protocol_or_none
        self.ssl_context = _handle_cert_context(
            cert=pki_data, password=password_bytes, ssl_protocol=ssl_protocol
        )
        super(PKIAdapter, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------
    def init_poolmanager(self, *args, **kwargs):
        if self.ssl_context:
            kwargs["ssl_context"] = self.ssl_context
        return super(PKIAdapter, self).init_poolmanager(*args, **kwargs)

    # ---------------------------------------------------------------------
    def proxy_manager_for(self, *args, **kwargs):
        if self.ssl_context:
            kwargs["ssl_context"] = self.ssl_context
        return super(PKIAdapter, self).proxy_manager_for(*args, **kwargs)

    # ---------------------------------------------------------------------
    def cert_verify(self, conn, url, verify, cert):
        check_hostname = self.ssl_context.check_hostname
        try:
            if verify is False:
                self.ssl_context.check_hostname = False
            return super(PKIAdapter, self).cert_verify(conn, url, verify, cert)
        finally:
            self.ssl_context.check_hostname = check_hostname

    # ---------------------------------------------------------------------
    def send(
        self,
        request,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
    ):
        check_hostname = self.ssl_context.check_hostname
        try:
            if verify is False:
                self.ssl_context.check_hostname = False
            return super(PKIAdapter, self).send(
                request, stream, timeout, verify, cert, proxies
            )
        finally:
            self.ssl_context.check_hostname = check_hostname


###########################################################################
class EsriHostHeaderSSLAdapter(HTTPAdapter):
    """
    A HTTPS Adapter for Python Requests that sets the hostname for certificate
    verification based on the Host header.

    This allows requesting the IP address directly via HTTPS without getting
    a "hostname doesn't match" exception.

    **modified to use TrustStore from requests-toolbelt library**

    Example usage:

        >>> s.mount('https://', HostHeaderSSLAdapter())
        >>> s.get("https://93.184.216.34", headers={"Host": "example.org"})

    """

    # ---------------------------------------------------------------------
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} >"

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"< {self.__class__.__name__} >"

    # ---------------------------------------------------------------------
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        return super().init_poolmanager(connections, maxsize, block, ssl_context=ctx)

    # ---------------------------------------------------------------------
    def send(self, request, **kwargs):
        # HTTP headers are case-insensitive (RFC 7230)
        host_header = None
        for header in request.headers:
            if header.lower() == "host":
                host_header = request.headers[header]
                break

        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        if host_header:
            connection_pool_kwargs["assert_hostname"] = host_header
        elif "assert_hostname" in connection_pool_kwargs:
            # an assert_hostname from a previous request may have been left
            connection_pool_kwargs.pop("assert_hostname", None)

        return super(EsriHostHeaderSSLAdapter, self).send(request, **kwargs)
