#!/bin/bash
$PYTHON ./build/manage_binaries.py copy --conda --python $PY_VER
$PYTHON ./src/setup.py install --conda-install-mode