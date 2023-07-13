import os
from pathlib import Path
from warnings import warn

from arcgis.features import GeoAccessor
from arcgis.geoenrichment import Country, enrich
from arcgis.geoenrichment._business_analyst._utils import (
    module_avail,
    local_business_analyst_avail,
)
from arcgis.gis import GIS

dir_data = Path(__file__).parent.parent / "geoenrich_data"

# load up the dotenv file
if module_avail("dotenv"):
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())

# start building up a list of sources to test
_src_lst = []
_src_nm_lst = []

# if the local environment is configured with arcpy (Pro), Business Analyst and local data
local_ba_avail = local_business_analyst_avail()

# if local_ba_avail:
#     _src_lst.append(GIS('Pro'))
#     _src_nm_lst.append('local')
# else:
#     warn('Cannot test the Geoenrichment module using local resources since ArcGIS Pro with the Business Analyst '
#          'extension with at least one country\'s data is installed')

# create an active connection to ArcGIS Online and add to the source list if possible
try:
    agol = GIS(profile="your_online_profile")
except:
    _agol_url, _agol_user, _agol_pass = (
        "https://geosaurus.maps.arcgis.com",
        "headless_testing",
        "Esr!3801",
    )
    if _agol_url and _agol_user and _agol_pass:
        agol = GIS(
            "https://geosaurus.maps.arcgis.com",
            username="headless_testing",
            password="Esr!3801",
        )
_src_lst.append(agol)
_src_nm_lst.append("agol")


def source():
    param = _src_lst[0]
    id = _src_nm_lst[0]
    return param


def usa_instance():
    source_inst = source()
    return Country.get("USA", gis=source_inst)
