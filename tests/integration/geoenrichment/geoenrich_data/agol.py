from configparser import ConfigParser
import os

from arcgis.gis import GIS
from arcgis.geoenrichment._business_analyst._utils import module_avail

__all__ = ["gis_agol"]

# if present, use python dotenv, but roll back to configparser if not
if module_avail("dotenv"):
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())

# try to load from environment variables - will all be None if not set or loaded
_agol_url, _agol_user, _agol_pass = (
    os.getenv("AGOL_URL"),
    os.getenv("AGOL_USERNAME"),
    os.getenv("AGOL_PASSWORD"),
)

# use configfile if still not set
if _agol_url is None and _agol_user is None and _agol_pass is None:
    config = ConfigParser()
    config.read('../config.ini')
    _agol_url, _agol_user, _agol_pass = (
        config["AGOL"]["URL"],
        config["AGOL"]["USERNAME"],
        config["AGOL"]["PASSWORD"],
    )

# create a connection to the GIS for testing
gis_agol = GIS(
    url=_agol_url,
    username=_agol_user,
    password=_agol_pass,
)
