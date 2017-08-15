#!/bin/bash
# cd ___output/linux-32
# find . -type f -exec anaconda upload {} \;
# cd ../linux-64
# find . -type f -exec anaconda upload {} \;

# hard coded upload
anaconda upload ___output/linux-32/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/linux-32/arcgis-1.2.1-py35_1.tar.bz2
anaconda upload ___output/linux-64/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/linux-64/arcgis-1.2.1-py35_1.tar.bz2
anaconda upload ___output/win-32/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/win-32/arcgis-1.2.1-py35_1.tar.bz2
anaconda upload ___output/win-64/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/win-64/arcgis-1.2.1-py35_1.tar.bz2
anaconda upload ___output/osx-64/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/osx-64/arcgis-1.2.1-py35_1.tar.bz2