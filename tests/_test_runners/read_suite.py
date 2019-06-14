import os
import glob
import re

import yaml

from utils._common import *

def read_suite(suite_file_path, 
               geosaurus_dir = GEOSAURUS_ROOT_DIR,
               arcgis_python_api_dir="/path/not/specified/"):
    """Reads in the specified "/path/to/suite.yaml" str path. Replaces the 
    {placeholder} tags with the correct full paths, unglobs any glob syntax 
    paths, removes paths from the blacklist, returns the newly parsed suite 
    dict object
    """
    suite = {}
    with open(suite_file_path, 'r') as f:
        suite = yaml.load(f)

    replace_placeholders(suite, GEOSAURUS_ROOT_DIR, arcgis_python_api_dir)
    unglob_paths(suite)
    remove_blacklist_paths(suite)
    return suite

def replace_placeholders(dict_, geosaurus_dir, arcgis_python_api_dir):
    """Replaces all {geosaurus_dir} and {arcgis_python_api_dir} placeholder
    tags in strings with the specified paths
    """
    if isinstance(dict_, dict):
        for key in dict_:
            value = dict_[key]
            if isinstance(value, dict):
                replace_placeholders(value, 
                                     geosaurus_dir, 
                                     arcgis_python_api_dir)
            elif isinstance(value, list):
                for i in range(0, len(value)):
                    if isinstance(value[i], str):
                        value[i] = os.path.normpath(value[i].format(
                            geosaurus_dir = geosaurus_dir,
                            arcgis_python_api_dir = arcgis_python_api_dir))

def unglob_paths(dict_):
    """Unglobs all globable lists of paths in the whole suite"""
    if isinstance(dict_, dict):
        for key in dict_:
            value = dict_[key]
            if isinstance(value, dict):
                unglob_paths(value)
            elif isinstance(value, list):
                new_list = []
                for preglob_path in value:
                    for postglob_path in glob.glob(preglob_path, 
                                                   recursive=True):
                        new_list.append(postglob_path)
                dict_[key] = new_list

def remove_blacklist_paths(suite):
    """Removes all matching blacklist items from the `paths` entry"""
    for tests_to_run_key in suite:
        if 'blacklist' not in suite[tests_to_run_key]['config']:
            continue
        blacklist = suite[tests_to_run_key]['config']['blacklist']
        for blacklist_path in blacklist:
            suite[tests_to_run_key]['paths'] = list(\
                path for path in suite[tests_to_run_key]['paths'] \
                if not path == blacklist_path)
