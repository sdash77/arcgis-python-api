ren ___output ___output.old
anaconda remove -f geonuma/arcgis/0.3/win-64/arcgis-0.3-py34_1.tar.bz2
anaconda remove -f geonuma/arcgis/0.3/win-64/arcgis-0.3-py35_1.tar.bz2
mkdir ___output
conda build arcgis
conda build --py 3.5 arcgis
conda convert -f --platform all C:\Users\rohit\Anaconda3\conda-bld\win-64\arcgis-0.3-py34_1.tar.bz2 -o ___output
conda convert -f --platform all C:\Users\rohit\Anaconda3\conda-bld\win-64\arcgis-0.3-py35_1.tar.bz2 -o ___output
