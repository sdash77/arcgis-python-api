import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
import os
import base64
import configparser
from functools import lru_cache
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def decode_value(value: bytes) -> str:
    if isinstance(value, str):
        value = value.encode()
    return base64.b64decode(value).decode()


@lru_cache(maxsize=100)
def get_config_parser() -> dict:
    """
    loads the configuration settings

    :returns: Dict
    """
    configs = [
        os.path.join(
            QALAB_ROOT_PATH,
            "esri_requests",
            "config.ini",
        ),
        os.path.join(os.path.dirname(__file__), "config.ini.txt"),
        os.path.join(os.path.dirname(__file__), "config.ini"),
        os.path.join(
            QALAB_ROOT_PATH,
            "esri_requests",
            "config.ini",
        ),
        os.path.join(
            QALAB_ROOT_PATH,
            "esri_requests",
            "config.ini.txt",
        ),
    ]
    for config in configs:
        if os.path.isfile(config):
            cp = configparser.ConfigParser()
            config = cp.read(config)
            return dict(cp)
    return {}


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

try:
    config = get_config_parser()
    URL = config['builtin_admin_account_info_kubes']['url']
    USERNAME = decode_value(
        config['builtin_admin_account_info_kubes']['username']
    )
    PASSWORD = decode_value(
        config['builtin_admin_account_info_kubes']['password']
    )
    SECURITY_IDX = int(
        config['builtin_admin_account_info_kubes']['security_idx']
    )
    SECURITY_ANS = decode_value(
        config['builtin_admin_account_info_kubes']['security_answer']
    )
    CONFIG_FAILED = False
except:
    CONFIG_FAILED = True


@unittest.skipIf(CONFIG_FAILED, reason='cannot find config.ini file.')
@integration_test
class TestKubernetesCertificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (
            GIS(
                url=URL,
                username=USERNAME,
                password=PASSWORD,
                verify_cert=False,
                trust_env=True,
                proxy=PROXIES,
                use_gen_token=True,
            ).users.me.update(
                security_question=SECURITY_IDX, security_answer=SECURITY_ANS
            )
        )

        cls.gis = GIS(
            url=URL,
            username=USERNAME,
            password=PASSWORD,
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_trust_certs(self):
        gis = self.gis
        security = gis.admin.security

        kubeCert = security.certificates
        assert kubeCert

        assert kubeCert.trust_certs


if __name__ == "__main__":
    unittest.main()
