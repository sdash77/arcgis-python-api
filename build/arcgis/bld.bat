set DEPENDENCY_ROOT_PATH=\\geosaurus.esri.com\Public\build\geosaurus2\windows\py%PY_VER%

set TRACKER_PATH=%DEPENDENCY_ROOT_PATH%\tracking-engine
ECHO Getting tracker artifacts from %TRACKER_PATH%
if not exist arcgis\learn\_tracking mkdir arcgis\learn\_tracking
copy %TRACKER_PATH%\* arcgis\learn\_tracking\ /Y

set KNN_PATH=%DEPENDENCY_ROOT_PATH%\knn
ECHO Getting knn artifacts from %KNN_PATH%
copy %KNN_PATH%\* arcgis\learn\_utils\ /Y

set NBAUTH_PATH=%DEPENDENCY_ROOT_PATH%\nbauth
ECHO Getting nbauth artifacts from %NBAUTH_PATH%
copy %NBAUTH_PATH%\* arcgis\gis\_impl\ /Y

set GRAPH_PATH=%DEPENDENCY_ROOT_PATH%\graph
ECHO Getting knowledge graph artifacts from %GRAPH_PATH%
copy %GRAPH_PATH%\* arcgis\graph\ /Y

"%PYTHON%" setup.py install --conda-install-mode
if errorlevel 1 exit 1
