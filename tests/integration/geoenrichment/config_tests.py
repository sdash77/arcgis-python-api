from configparser import ConfigParser
import os
from pathlib import Path
from warnings import warn

from arcgis.geoenrichment import Country
from arcgis.geoenrichment._business_analyst._utils import (
    local_business_analyst_avail,
    local_ba_data_avail,
    module_avail,
)
from arcgis.gis import GIS
import pytest

dir_data = Path(__file__).parent / "geoenrich_data"

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
    config.read('./config.ini')
    _agol_url, _agol_user, _agol_pass = (
        config["AGOL"]["URL"],
        config["AGOL"]["USERNAME"],
        config["AGOL"]["PASSWORD"],
    )

# start building up a list of sources to test
_src_lst = []
_src_nm_lst = []

# if the local environment is configured with arcpy (Pro), Business Analyst and local data
local_ba_avail = local_business_analyst_avail() and local_ba_data_avail()

if local_ba_avail:
    _src_lst.append(GIS("Pro"))
    _src_nm_lst.append("local")
else:
    warn(
        "Cannot test the Geoenrichment module using local resources since ArcGIS Pro with the Business Analyst "
        "extension with at least one country's data is installed"
    )

# create an active connection to ArcGIS Online and add to the source list if possible
if _agol_url and _agol_user and _agol_pass:
    agol = GIS(
        os.getenv("AGOL_URL"),
        username=os.getenv("AGOL_USERNAME"),
        password=os.getenv("AGOL_PASSWORD"),
    )
    _src_lst.append(agol)
    _src_nm_lst.append("agol")
else:
    warn("Cannot test ArcGIS Online because cannot load URL and credentials from config.ini.")


@pytest.fixture(scope="module", params=_src_lst, ids=_src_nm_lst)
def source(request):
    yield request.param


@pytest.fixture
def usa_instance(source):
    yield Country.get("USA", gis=source)
