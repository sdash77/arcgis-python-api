import sys
import os
import argparse
import logging
log = logging.getLogger()

#import geosaurus/automation/stage_notebooks_for_dev_web_repo
geosaurus_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
    '..', '..'))
sys.path.append(geosaurus_root_dir)
from automation import stage_notebooks_for_dev_web_repo

def _main():
    args = _parse_args()
    stage_notebooks_for_dev_web_repo(notebooks_root_dir = args.notebooks_repo,
                                     output_dir = args.developers_repo,
                                     log_func = log.info)

def _parse_args():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description = ""\
    "Convert all notebooks in the specified arcgis-python-api repo to a "\
    "format that the arcgis-for-developers repo can work with. See "\
    "github.com/ArcGIS/geosaurus/wiki/Modifying-the-Developers-Website "\
    "for info on how to use this tool, how the CI system uses it, etc.")
    parser.add_argument('-n', '--notebooks-repo', required=True,
        help="Path to arcgis-python-api repo")
    parser.add_argument('-d', '--developers-repo', required=True,
        help="Path to arcgis-for-developers repo")
    return parser.parse_args()

if __name__ == "__main__":
    exit(_main())
