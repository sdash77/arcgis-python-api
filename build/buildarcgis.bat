ren ___output ___output.old
anaconda remove -f geonuma/arcgis/1.0/win-64/arcgis-1.0-py34_1.tar.bz2
anaconda remove -f geonuma/arcgis/1.0/win-64/arcgis-1.0-py35_1.tar.bz2
mkdir ___output
conda build arcgis
conda build --py 3.5 arcgis
