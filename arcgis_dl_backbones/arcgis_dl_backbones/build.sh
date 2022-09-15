$PYTHON -m pip install . --no-deps --ignore-installed -vv 
$PYTHON $SP_DIR/arcgis_dl_backbones/cache.py
$PYTHON $SP_DIR/arcgis_dl_backbones/package.py
if errorlevel 1 exit 1