#!/usr/bin/env python

# Thanks @takluyver for your cite2c install.py.
# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import argparse
from os.path import dirname, abspath, join as pjoin

from notebook.nbextensions import install_nbextension
from notebook.services.config import ConfigManager

def install(user=False, symlink=False, enable=False):
    """Install the widget nbextension and optionally enable it.

    Parameters
    ----------
    user: bool
        Install for current user instead of system-wide.
    symlink: bool
        Symlink instead of copy (for development).
    """
    widgetsdir = pjoin(dirname(abspath(__file__)), 'widgets')
    install_nbextension(widgetsdir, destination='arcgis', user=user, symlink=symlink)

    cm = ConfigManager()
    cm.update('notebook', {
        "load_extensions": {
            "arcgis/mapview": True,
        }
    })


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Installs the ArcGIS IPython widgets")
    parser.add_argument("-u", "--user", help="Install as current user instead of system-wide", action="store_true")
    parser.add_argument("-s", "--symlink", help="Symlink instead of copying files", action="store_true")
    args = parser.parse_args()

    install(user=args.user, symlink=args.symlink)
