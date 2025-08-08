# -------------------------------------------------------------------------------
# Name:        dino_configs.py
# Purpose:     To read the config or ini files for the test fixtures
# -------------------------------------------------------------------------------
import configparser
import os
from pathlib import Path

current_file_path = Path(os.path.realpath(__file__))
_config_reader = configparser.ConfigParser()


class DinoConfigs:
    _unittest_path = current_file_path.parent.parent
    root_init_file = _unittest_path.joinpath("unittest.ini").__str__()
    _config_reader.read(root_init_file, "UTF-8")

    portal_list_file = _unittest_path.joinpath(
        _config_reader["portal_list"]["inifile"]
    ).__str__()
