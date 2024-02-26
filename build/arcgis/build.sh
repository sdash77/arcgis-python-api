#!/bin/bash
cd src

DEPENDENCY_HOST=http://geosaurus.esri.com
DEPENDENCY_PATH=build/geosaurus2/linux/py${PY_VER}
DEPENDENCY_ROOT_URL=$DEPENDENCY_HOST/$DEPENDENCY_PATH

TRACKING_ENGINE_URL=$DEPENDENCY_ROOT_URL/tracking-engine
wget -e robots=off -l1 -r -np -nH -R "index.html" $TRACKING_ENGINE_URL -q
mkdir -p arcgis/learn/_tracking
cp $DEPENDENCY_PATH/tracking-engine/* arcgis/learn/_tracking/

KNN_URL=$DEPENDENCY_ROOT_URL/knn
wget -e robots=off -l1 -r -np -nH -R "index.html" $KNN_URL -q
cp $DEPENDENCY_PATH/knn/* arcgis/learn/_utils/

NBAUTH_URL=$DEPENDENCY_ROOT_URL/nbauth
wget -e robots=off -l1 -r -np -nH -R "index.html" $NBAUTH_URL -q
cp $DEPENDENCY_PATH/nbauth/* arcgis/gis/_impl/

GRAPH_URL=$DEPENDENCY_ROOT_URL/graph
wget -e robots=off -l1 -r -np -nH -R "index.html" $GRAPH_URL -q
cp $DEPENDENCY_PATH/graph/* arcgis/graph/

rm -rf $DEPENDENCY_PATH

$PYTHON setup.py install --conda-install-mode
