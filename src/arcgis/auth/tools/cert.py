from __future__ import annotations
import os
import ssl
import logging
import datetime as _dt
import tempfile
import importlib
from enum import Enum
from datetime import timezone as _tz
import truststore
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from cryptography.x509.base import Certificate

from requests.adapters import (
    HTTPAdapter,
    DEFAULT_POOLSIZE,
    DEFAULT_RETRIES,
    DEFAULT_POOLBLOCK,
)


__log__ = logging.getLogger()

__all__ = [
    "SSLProtocol",
    "create_custom_ssl_context",
    "TruststoreAdapter",
    "SSLContextAdapter",
]


###########################################################################
class SSLProtocol(Enum):
    PROTOCOL_TLS = getattr(ssl, "PROTOCOL_TLS")
    PROTOCOL_TLSv1 = getattr(ssl, "PROTOCOL_TLSv1")
    PROTOCOL_TLSv1_1 = getattr(ssl, "PROTOCOL_TLSv1_1")
    PROTOCOL_TLSv1_2 = getattr(ssl, "PROTOCOL_TLSv1_2")
    PROTOCOL_TLS_CLIENT = getattr(ssl, "PROTOCOL_TLS_CLIENT")


# -------------------------------------------------------------------------
def check_cert_date(cert: Certificate | None) -> bool:
    """verifies certificate is valid based on date"""
    if not cert:
        __log__.warning("Not certificate provided, skipping.")
        return True
    elif cert.not_valid_after_utc < _dt.datetime.now(tz=_tz.utc):
        __log__.warning(
            f"The x509 certificate is expired. Expired on: {cert.not_valid_after}"
        )
        return False
    return True


# -------------------------------------------------------------------------
def create_custom_ssl_context(
    protocol: SSLProtocol = SSLProtocol.PROTOCOL_TLS_CLIENT,
    ssl_certificate: str | list[str] | None = None,
    verify_mode: ssl.VerifyMode | None = None,
    pkcs12_data: str | bytes | None = None,
    pkcs12_password: str | bytes | None = None,
    check_hostname: bool = True,
    add_certifi_cert: bool = False,
) -> truststore.SSLContext:
    """
    Creates an SSL Context object that can be used in `httpx` or `requests` that contains the system
    certificates and a set of custom CA bundles.  The method also provides the ability to inject x.509 (pki)
    certificates into a chain.



    :returns: truststore.SSLContext
    """
    if verify_mode is None:
        verify_mode = ssl.VerifyMode.CERT_REQUIRED
    if isinstance(pkcs12_password, str):
        # ensure the password is in bytes for cryptography
        pkcs12_password: bytes = pkcs12_password.encode()

    if not protocol in SSLProtocol:
        # verify if the PROTOCOL is supported.
        raise ValueError("The protocol must be a member of the `ssl` protocal library.")

    if check_hostname == True and verify_mode == 0:
        __log__.warning("check_hostname must be False when verify is False.")
        check_hostname = False

    tls_verify_mode: ssl.VerifyMode | None = verify_mode.value
    #  Create the SSLContext object

    ssl_context: truststore.SSLContext = truststore.SSLContext(protocol.value)
    ssl_context.check_hostname = check_hostname
    ssl_context.verify_mode = tls_verify_mode

    #  loads certifi into the SSLContext
    if add_certifi_cert and importlib.util.find_spec("certifi"):
        import certifi

        ssl_context.load_verify_locations(cafile=certifi.where())
    elif add_certifi_cert and importlib.util.find_spec("certifi") is None:
        __log__.warning("certifi is not installed, skipping the load.")
    #  loads any user provided CA files
    if isinstance(ssl_certificate, str):
        ssl_context.load_verify_locations(cafile=ssl_certificate)
    elif isinstance(ssl_certificate, (list, tuple)):
        for cert in ssl_certificate:
            ssl_context.load_verify_locations(cafile=cert)

    # adds x.509 certificates (handles PKI)
    if pkcs12_data and pkcs12_password:
        (private_key, cert, ca_certs) = load_key_and_certificates(
            pkcs12_data, pkcs12_password
        )
        if check_cert_date(cert) == False:
            raise Exception("The pksc12 certificate provided is expired.")
        with tempfile.NamedTemporaryFile(delete=False) as c:
            try:
                private_bytes = private_key.private_bytes(
                    Encoding.PEM,
                    PrivateFormat.TraditionalOpenSSL,
                    serialization.NoEncryption(),
                )
                c.write(private_bytes)

                public_bytes = cert.public_bytes(Encoding.PEM)
                c.write(public_bytes)

                if ca_certs:
                    for ca_cert in ca_certs:
                        check_cert_date(ca_cert)
                        ca_public_bytes = ca_cert.public_bytes(Encoding.PEM)
                        c.write(ca_public_bytes)

                c.flush()
                c.close()
                ssl_context.load_cert_chain(c.name, password=pkcs12_password)
            finally:
                os.remove(c.name)
    return ssl_context


###########################################################################
class TruststoreAdapter(HTTPAdapter):
    """An adapter for requests <=2.31.0.  This supplies the a custom ssl_context to a set of requests."""

    custom_context: truststore.SSLContext | ssl.SSLContext = None

    def __init__(
        self,
        pool_connections=DEFAULT_POOLSIZE,
        pool_maxsize=DEFAULT_POOLSIZE,
        max_retries=DEFAULT_RETRIES,
        pool_block=DEFAULT_POOLBLOCK,
        ssl_context: truststore.SSLContext | ssl.SSLContext | None = None,
    ):

        ssl_context = ssl_context or truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.custom_context = ssl_context

        super().__init__(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
            pool_block=pool_block,
        )

    # ---------------------------------------------------------------------
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} >"

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"< {self.__class__.__name__} >"

    # ---------------------------------------------------------------------
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = self.custom_context
        return super().init_poolmanager(connections, maxsize, block, ssl_context=ctx)


###########################################################################
class SSLContextAdapter(HTTPAdapter):
    """
    Modern `requests` adapter to handle the passing of custom `SSLContext` to
    a `Session` using a custom adapter.



    """

    def __init__(
        self,
        pool_connections=DEFAULT_POOLSIZE,
        pool_maxsize=DEFAULT_POOLSIZE,
        max_retries=DEFAULT_RETRIES,
        pool_block=DEFAULT_POOLBLOCK,
        ssl_context: truststore.SSLContext | ssl.SSLContext | None = None,
    ):
        super().__init__(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
            pool_block=pool_block,
        )
        self.custom_context = ssl_context

    def build_connection_pool_key_attributes(self, request, verify, cert=None):
        (
            host_params,
            pool_kwargs,
        ) = super().build_connection_pool_key_attributes(request, verify, cert)
        if self.custom_context:
            pool_kwargs["cert_reqs"] = self.custom_context.verify_mode.name
            pool_kwargs["ssl_context"] = self.custom_context
        return host_params, pool_kwargs
