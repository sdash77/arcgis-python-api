set TRACKER_PATH=\\DEV0000935\build_files\tracking-engine\win_py%PY_VER%
ECHO Getting tracker artifacts from %TRACKER_PATH%
if not exist arcgis\learn\_tracking mkdir arcgis\learn\_tracking
copy %TRACKER_PATH%\_track_processor.pyd arcgis\learn\_tracking\_track_processor.pyd /Y
copy %TRACKER_PATH%\tracking_engine.dll arcgis\learn\_tracking\tracking_engine.dll /Y


set KNN_PATH=\\DEV0000935\build_files\knn\win_py%PY_VER%
ECHO Getting knn artifacts from %KNN_PATH%
copy %KNN_PATH%\* arcgis\learn\_utils\ /Y

"%PYTHON%" setup.py install --conda-install-mode
if errorlevel 1 exit 1
