import os
import configparser
from functools import lru_cache


@lru_cache(maxsize=100)
def get_config_parser() -> dict:
    """
    loads the configuration settings

    :returns: Dict
    """
    configs = [
        os.path.join(
            r"\\qalab_server\pydata\v109\geosaurus\esri_requests", "config.ini"
        ),
        os.path.join(os.path.dirname(__file__), "config.ini.txt"),
        os.path.join(os.path.dirname(__file__), "config.ini"),
        os.path.join(
            r"\\qalab_server\pydata\v109\geosaurus\esri_requests", "config.ini"
        ),
        os.path.join(
            r"\\qalab_server\pydata\v109\geosaurus\esri_requests", "config.ini.txt"
        ),
    ]
    for config in configs:
        if os.path.isfile(config):
            cp = configparser.ConfigParser()
            config = cp.read(config)
            return dict(cp)
    return {}
