import importlib
import os

from arcgis.gis import GIS

__all__ = ["gis_agol"]

# get dotenv if available and load the dotenv file
if importlib.util.find_spec("dotenv") is not None:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())

# ensure all keys are available
key_lst = ["AGOL_URL", "AGOL_USERNAME", "AGOL_PASSWORD"]
for key in key_lst:
    assert (
        os.getenv(key) is not None
    ), f"The environment variable, {key}, is not available."

# create a connection to the GIS for testing
gis_agol = GIS(
    url=os.getenv(key_lst[0]),
    username=os.getenv(key_lst[1]),
    password=os.getenv(key_lst[2]),
)
