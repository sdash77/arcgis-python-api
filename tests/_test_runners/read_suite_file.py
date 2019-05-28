import os
import glob

import yaml

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..',
    '..'))

def read_suite_file(suite_file_path, 
                    geosaurus_dir = GEOSAURUS_ROOT_DIR,
                    arcgis_python_api_dir="/path/not/specified/"):
    """Reads in the specified /path/to/yaml/, replaces the {placeholder} tags
    with the correct full paths, unglobs any glob syntax paths, removes paths
    from the blacklist, returns the suite dict object
    """
    suite = {}
    with open(suite_file_path, 'r') as f:
        suite = yaml.load(f)
    _replace_placeholders(suite, GEOSAURUS_ROOT_DIR, arcgis_python_api_dir)
    _unglob_paths(suite)
    _remove_blacklist_paths(suite)
    return suite

def _replace_placeholders(dict_, geosaurus_dir, arcgis_python_api_dir):
    """Replaces all {geosaurus_dir} and {arcgis_python_api_dir} placeholder
    tags in strings with the specified paths
    """
    if isinstance(dict_, dict):
        for key in dict_:
            value = dict_[key]
            if isinstance(value, dict):
                _replace_placeholders(value, 
                                      geosaurus_dir, 
                                      arcgis_python_api_dir)
            elif isinstance(value, list):
                for i in range(0, len(value)):
                    if isinstance(value[i], str):
                        value[i] = os.path.normpath(value[i].format(
                            geosaurus_dir = geosaurus_dir,
                            arcgis_python_api_dir = arcgis_python_api_dir))

def _unglob_paths(suite):
        for tests_to_run_key in suite:
            new_paths_list = []
            for path in suite[tests_to_run_key]['paths']:
                new_paths_list += glob.glob(path, recursive=True)
            suite[tests_to_run_key]['paths'] = new_paths_list

def _remove_blacklist_paths(suite):
    return
