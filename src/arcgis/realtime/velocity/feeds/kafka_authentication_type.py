from dataclasses import dataclass
from typing import Dict, ClassVar


@dataclass
class _KafkaAuthenticationType:
    _auth_type: ClassVar[str]

    def _build(self, feed_or_source_name: str) -> Dict[str, str]:
        raise NotImplementedError


@dataclass
class NoAuth(_KafkaAuthenticationType):
    _auth_type: ClassVar[str] = "none"

    def _build(self, feed_or_source_name: str) -> Dict[str, str]:
        return {f"{feed_or_source_name}.authenticationType": self._auth_type}


@dataclass
class SASLPlain(_KafkaAuthenticationType):
    _auth_type: ClassVar[str] = "saslPlain"

    username: str
    password: str

    def _build(self, feed_or_source_name: str) -> Dict[str, str]:
        return {
            f"{feed_or_source_name}.authenticationType": self._auth_type,
            f"{feed_or_source_name}.username": self._auth_type,
            f"{feed_or_source_name}.password": self._auth_type,
        }
