#!/bin/bash
cd src

$PYTHON ../build/manage_binaries.py copy --conda --python $PY_VER
$PYTHON setup.py install --conda-install-mode