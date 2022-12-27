#!/bin/bash
DEPENDENCY_ROOT_PATH=$RECIPE_DIR/bin/linux/py${PY_VER}

TRACKER_PATH=$DEPENDENCY_ROOT_PATH/tracking-engine
mkdir -p arcgis/learn/_tracking
cp $TRACKER_PATH/* arcgis/learn/_tracking/

KNN_PATH=$DEPENDENCY_ROOT_PATH/knn
cp $KNN_PATH/* arcgis/learn/_utils/

NBAUTH_PATH=$DEPENDENCY_ROOT_PATH/nbauth
cp $NBAUTH_PATH/* arcgis/gis/_impl/

GRAPH_PATH=$DEPENDENCY_ROOT_PATH/graph
cp $GRAPH_PATH/* arcgis/graph/

$PYTHON setup.py install --conda-install-mode
