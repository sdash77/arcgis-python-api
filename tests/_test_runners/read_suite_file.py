import os
import glob
import re


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
            for preglob_path in suite[tests_to_run_key]['paths']:
                for postglob_path in glob.glob(preglob_path, recursive=True):
                    new_paths_list.append(os.path.normpath(postglob_path))

            suite[tests_to_run_key]['paths'] = new_paths_list

def _remove_blacklist_paths(suite):
    print(f"about to apply blacklist to {suite}")
    for tests_to_run_key in suite:
        if 'blacklist_regexes' not in suite[tests_to_run_key]['config']:
            continue
        blacklist = suite[tests_to_run_key]['config']['blacklist_regexes']
        for blacklist_regex in blacklist:
            suite[tests_to_run_key]['paths'] = list(\
                path for path in suite[tests_to_run_key]['paths'] \
                if not re.match(blacklist_regex, re.escape(path)))
