import os 

from __init__ import GEOSAURUS_ROOT_DIR

def build_documentation():
    print("Starting to build the documentation...")

    if os.name == 'posix':
        _build_doc_for_unix()
    elif os.name == 'nt':
        _build_doc_for_windows()
    else:
        raise RuntimeError("Doc building not supported on this platform")

    print("Documentation building finished! Any results in {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR, 'automation', 'staging')))

def _build_doc_for_unix():
    print("Building for *nix system...")

def _build_doc_for_windows():
    print("Building for Windows system...")
