#!/bin/bash

wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/_track_processor.so -q && wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/_track_processor.so -O arcgis/learn/_tracking/_track_processor.so
wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/libTrackingEngine.so -q && wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/libTrackingEngine.so -O arcgis/learn/_tracking/libTrackingEngine.so

$PYTHON setup.py install --conda-install-mode
