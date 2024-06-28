cd src

"%PYTHON%" ..\build\manage_binaries.py copy --conda --python %PY_VER%
if errorlevel 1 exit 1
"%PYTHON%" setup.py install --conda-install-mode
if errorlevel 1 exit 1
