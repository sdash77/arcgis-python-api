import os
import glob
import re

import yaml

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..',
    '..'))

def read_suite(suite, 
               geosaurus_dir = GEOSAURUS_ROOT_DIR,
               arcgis_python_api_dir="/path/not/specified/"):
    """Reads in the specified "/path/to/suite.yaml" str path OR a dict 
    representation of a suite.yaml file. Replaces the {placeholder} tags
    with the correct full paths, unglobs any glob syntax paths, removes paths
    from the blacklist, returns the newly parsed suite dict object
    """
    output_suite = {}
    if isinstance(suite, str):
        with open(suite, 'r') as f:
            output_suite = yaml.load(f)
    elif isinstance(suite, dict):
        output_suite = suite

    _replace_placeholders(output_suite, GEOSAURUS_ROOT_DIR, arcgis_python_api_dir)
    _unglob_paths(output_suite)
    _remove_blacklist_paths(output_suite)
    return output_suite

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

def _unglob_paths(dict_):
    """Unglobs all globable lists of paths in the whole suite"""
    if isinstance(dict_, dict):
        for key in dict_:
            value = dict_[key]
            if isinstance(value, dict):
                _unglob_paths(value)
            elif isinstance(value, list):
                new_list = []
                for preglob_path in value:
                    for postglob_path in glob.glob(preglob_path, 
                                                   recursive=True):
                        new_list.append(postglob_path)
                dict_[key] = new_list

def _remove_blacklist_paths(output_suite):
    """Removes all matching blacklist items from the `paths` entry"""
    for tests_to_run_key in output_suite:
        if 'blacklist' not in output_suite[tests_to_run_key]['config']:
            continue
        blacklist = output_suite[tests_to_run_key]['config']['blacklist']
        for blacklist_path in blacklist:
            output_suite[tests_to_run_key]['paths'] = list(\
                path for path in output_suite[tests_to_run_key]['paths'] \
                if not path == blacklist_path)
