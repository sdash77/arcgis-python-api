#!/bin/bash
cd src

$PYTHON ../build/manage_binaries.py --conda --python $PY_VER
$PYTHON setup.py install --conda-install-mode