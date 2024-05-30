import os
import pathlib

# default unc path does not work on Linux (must be mounted)
# or on Windows if the executing user does not have permission to access
_DEFAULT_QALAB_ROOT_UNC = r'\\qalab_server\pydata\v109\geosaurus'
QALAB_ROOT_PATH = os.environ.get('QALAB_ROOT_PATH', _DEFAULT_QALAB_ROOT_UNC)

_INTEGRATION_TESTS_ROOT_PATH = pathlib.Path(os.path.dirname(__file__))
_TESTS_ROOT_PATH = _INTEGRATION_TESTS_ROOT_PATH.parent
_TESTS_RESOURCES_ROOT_PATH = _TESTS_ROOT_PATH / 'resources'
# allow overriding the path to the resources folder
# defaults to `geosaurus/tests/resources`
RESOURCES_ROOT_PATH = os.environ.get('GEOSAURUS_RESOURCES_ROOT_PATH', str(_TESTS_RESOURCES_ROOT_PATH))

def get_resource_path(relative_path, verify=True):
    resource = pathlib.Path(RESOURCES_ROOT_PATH) / relative_path
    if verify and not resource.exists():
        raise FileNotFoundError(f"Resource not found: {resource}")
    return str(resource)