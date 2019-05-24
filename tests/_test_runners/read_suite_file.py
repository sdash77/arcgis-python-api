import os

import yaml

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..',
    '..'))

def read_suite_file(suite_file_path, 
                    geosaurus_dir = GEOSAURUS_ROOT_DIR,
                    arcgis_python_api_dir="/path/not/specified/"):
    """Reads in the specified /path/to/yaml/, replaces the {placeholder} tags
    with the correct full paths, returns a dict object
    """
    suite = {}
    with open(suite_file_path, 'r') as f:
        suite = yaml.load(f)
    _complete_paths(suite, GEOSAURUS_ROOT_DIR, arcgis_python_api_dir)
    return suite

def _complete_paths(dict_, geosaurus_dir, arcgis_python_api_dir):
    if isinstance(dict_, dict):
        for key in dict_:
            value = dict_[key]
            if isinstance(value, dict):
                _complete_paths(value, geosaurus_dir, arcgis_python_api_dir)
            elif isinstance(value, list):
                for i in range(0, len(value)):
                    if isinstance(value[i], str):
                        value[i] = os.path.normpath(value[i].format(
                            geosaurus_dir = geosaurus_dir,
                            arcgis_python_api_dir = arcgis_python_api_dir))

