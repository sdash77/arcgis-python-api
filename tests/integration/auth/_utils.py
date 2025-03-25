import os
import base64
import configparser
from functools import lru_cache
from integration.config import QALAB_ROOT_PATH


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
