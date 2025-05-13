#!/bin/bash
$PYTHON ./build/manage_binaries.py copy --conda --python $PY_VER
$PYTHON -m pip install ./src --no-deps --no-build-isolation