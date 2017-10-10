import os

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..'))

STAGING_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "automation",
    "staging"))
