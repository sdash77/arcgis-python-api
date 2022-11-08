#!/bin/bash

wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/_track_processor.so -q && wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/_track_processor.so -O arcgis/learn/_tracking/_track_processor.so
wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/libTrackingEngine.so -q && wget http://zion:8002/build_files/tracking-engine/py${PY_VER}_linux/libTrackingEngine.so -O arcgis/learn/_tracking/libTrackingEngine.so

INSTALL_DIR=build_files/knn/py${PY_VER}_linux/
wget -e robots=off -l1 -r -np -nH -R "index.html" http://zion:8002/build_files/knn/py${PY_VER}_linux/ -q
mv ${INSTALL_DIR}*.so ${INSTALL_DIR}*.py -t arcgis/learn/_utils/
rm -rf build_files

$PYTHON setup.py install --conda-install-mode
