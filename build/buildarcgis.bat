ren ___output ___output.old
rem anaconda remove -f geonuma/arcgis/1.0/win-64/arcgis-1.0-py34_1.tar.bz2
rem anaconda remove -f geonuma/arcgis/1.0/win-64/arcgis-1.0-py35_1.tar.bz2
mkdir ___output
conda build --py 3.6 arcgis
conda build --py 3.5 arcgis
conda convert -f -p win-32 C:\Users\rohit\Anaconda3\conda-bld\win-64\arcgis-1.0.1-py35_1.tar.bz2 -o ___output
conda convert -f -p win-32 C:\Users\rohit\Anaconda3\conda-bld\win-64\arcgis-1.0.1-py36_1.tar.bz2 -o ___output