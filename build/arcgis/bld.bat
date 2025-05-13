"%PYTHON%" .\build\manage_binaries.py copy --conda --python %PY_VER%
if errorlevel 1 exit 1
"%PYTHON%" -m pip install .\src --no-deps --no-build-isolation
if errorlevel 1 exit 1
