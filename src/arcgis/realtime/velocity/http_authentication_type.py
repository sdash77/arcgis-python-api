from dataclasses import dataclass, asdict, field
from typing import Dict, Union, Optional, Any, ClassVar

@dataclass
class _HttpAuthenticationType():
    _auth_type: ClassVar[str]

    def _build(self, feed_or_source_name: str) -> Dict[str, str]:
        raise NotImplementedError

@dataclass
class NoAuth(_HttpAuthenticationType):
    _auth_type: ClassVar[str] = "noauth"

    def _build(self, feed_or_source_name: str) -> Dict[str, str]:
        return {
            f"{feed_or_source_name}.httpAuthenticationType": self._auth_type
        }

@dataclass
class BasicAuth(_HttpAuthenticationType):
    _auth_type: ClassVar[str] = "basicauth"

    username: str
    password: str

    def _build(self, feed_or_source_name: str) -> Dict[str, str]:
        return {
            f"{feed_or_source_name}.httpAuthenticationType": self._auth_type,
            f"{feed_or_source_name}.username": self.username,
            f"{feed_or_source_name}.password": self.password
        }


@dataclass
class CertificateAuth(_HttpAuthenticationType):
    _auth_type: ClassVar[str] = "certificateauth"

    pfx_file_http_location: str
    password: str

    def _build(self, feed_or_source_name: str) -> Dict[str, str]:
        return {
            f"{feed_or_source_name}.httpAuthenticationType": self._auth_type,
            f"{feed_or_source_name}.password": self.password,
            f"{feed_or_source_name}.pfxLocation": self.pfx_file_http_location
        }