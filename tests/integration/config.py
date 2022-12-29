from os import environ

# default unc path does not work on Linux (must be mounted)
# or on Windows if the executing user does not have permission to access
_DEFAULT_QALAB_ROOT_UNC = r'\\qalab_server\pydata\v109\geosaurus'
QALAB_ROOT_PATH = environ.get('QALAB_ROOT_PATH', _DEFAULT_QALAB_ROOT_UNC)
