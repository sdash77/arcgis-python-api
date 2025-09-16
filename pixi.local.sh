python -m pip install ./src --no-deps

if [[ -d ../geoserpent && ! -z $(which npm) ]]; then
    python -m pip install ../geoserpent/arcgis-mapping/src --no-deps
fi
