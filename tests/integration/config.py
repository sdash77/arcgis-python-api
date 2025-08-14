import os
import pathlib
import tempfile

import json
import requests
import shutil
import urllib.parse
import uuid

INTEGRATION_TEST_ITEM_TAG = "ntgrtn-tst"

# default unc path does not work on Linux (must be mounted)
# or on Windows if the executing user does not have permission to access
_DEFAULT_QALAB_ROOT_UNC = r"\\qalab_server\pydata\v109\geosaurus"
QALAB_ROOT_PATH = os.environ.get("QALAB_ROOT_PATH", _DEFAULT_QALAB_ROOT_UNC)

_INTEGRATION_TESTS_ROOT_PATH = pathlib.Path(os.path.dirname(__file__))
_TESTS_ROOT_PATH = _INTEGRATION_TESTS_ROOT_PATH.parent
_TESTS_RESOURCES_ROOT_PATH = _TESTS_ROOT_PATH / "resources"
# allow overriding the path to the resources folder
# defaults to `geosaurus/tests/resources`
RESOURCES_ROOT_PATH = os.environ.get(
    "GEOSAURUS_RESOURCES_ROOT_PATH", str(_TESTS_RESOURCES_ROOT_PATH)
)
WEB_RESOURCE_ROOT_PATH = os.environ.get(
    "GEOSAURUS_RESOURCES_WEB_ROOT", "https://esri-forge.python.geocloud.com/_/data/"
)


def get_resource_path(relative_path=None, verify=True, unique_copy=False):
    """
    Get the absolute path to a resource file within this repository. e.g. `./geosaurus/tests/resources`

    If `relative_path` is None, it returns the root path of the resources.
    If `verify` is True, it checks if the resource exists and raises FileNotFoundError if it does not.
    If `unique_copy` is True, it creates a unique copy of the resource in a temporary directory.
    """
    relative_path = relative_path or '' # use empty string for root path
    # Normalize the path to use forward slashes and remove leading slashes
    relative_path = relative_path.replace('\\', '/').lstrip('/')
    resource = pathlib.Path(RESOURCES_ROOT_PATH) / (relative_path or '')
    if verify and not resource.exists():
        raise FileNotFoundError(f"Resource not found: {resource}")
    if unique_copy:
        temp_dir = tempfile.mkdtemp()
        unique_name = f"{resource.stem}_{uuid.uuid4().hex}{resource.suffix}"
        temp_resource_copy = pathlib.Path(temp_dir, unique_name)
        shutil.copy(resource, temp_resource_copy)
        resource = temp_resource_copy
    return str(resource)

def get_json_resource(relative_path):
    """
    Load json resource from the resources folder.
    """
    resource_path = get_resource_path(relative_path, verify=True)
    with open(resource_path) as f:
        data = json.load(f)
    return data


def copy_as_tempfile(staging_data_path: str):
    resource = pathlib.Path(staging_data_path)
    temp_dir = tempfile.mkdtemp()
    unique_name = f"{resource.stem}_{uuid.uuid4().hex}{resource.suffix}"
    temp_resource_copy = pathlib.Path(temp_dir, unique_name)
    shutil.copy(resource, temp_resource_copy)
    return str(temp_resource_copy)


def get_web_resource_path(relative_path, unique_copy=False):
    _resource_cache_path = f"_web/{relative_path}"
    try:
        cached_resource = get_resource_path(
            _resource_cache_path, verify=True, unique_copy=unique_copy
        )
        return cached_resource
    except FileNotFoundError:
        resource_url = urllib.parse.urljoin(WEB_RESOURCE_ROOT_PATH, relative_path)
        try:
            response = requests.get(resource_url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise FileNotFoundError(f"Failed to fetch web resource: {relative_path}") from e
    
        # save the resource to the cache
        content = response.content
        resource_path = get_resource_path(_resource_cache_path, verify=False)
        os.makedirs(os.path.dirname(resource_path), exist_ok=True)
        # TODO consider streaming the content to the file
        # first pass is only working with files <1MB
        with open(resource_path, "wb") as f:
            f.write(content)
        return get_resource_path(_resource_cache_path, verify=True, unique_copy=unique_copy)
