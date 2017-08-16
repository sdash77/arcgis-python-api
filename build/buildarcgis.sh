#!/bin/bash
mv ___output ___output.old
logged_in_user='atmamani'
ver_to_remove='1.2.0'
ver_to_build='1.2.1'
# logged_in_user = 'geonuma'

# Remove old packages
# anaconda remove -f $logged_in_user/arcgis/1.2.0/osx-64/arcgis-1.2.0-py36_1.tar.bz2
# anaconda remove -f $logged_in_user/arcgis/1.2.0/osx-64/arcgis-1.2.0-py35_1.tar.bz2
# anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-64/arcgis-1.2.0-py36_1.tar.bz2
# anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-64/arcgis-1.2.0-py35_1.tar.bz2
# anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-32/arcgis-1.2.0-py36_1.tar.bz2
# anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-32/arcgis-1.2.0-py35_1.tar.bz2

mkdir ___output
# conda build arcgis
conda build --py 3.5 arcgis
conda build --py 3.6 arcgis

# convert packages to linux
conda convert -f -p linux-32 ~/anaconda/conda-bld/osx-64/arcgis-1.2.1-py35_1.tar.bz2 -o ___output
conda convert -f -p linux-32 ~/anaconda/conda-bld/osx-64/arcgis-1.2.1-py36_1.tar.bz2 -o ___output
conda convert -f -p linux-64 ~/anaconda/conda-bld/osx-64/arcgis-1.2.1-py35_1.tar.bz2 -o ___output
conda convert -f -p linux-64 ~/anaconda/conda-bld/osx-64/arcgis-1.2.1-py36_1.tar.bz2 -o ___output

#copy the osx package to ___output
mkdir ___output/osx-64
cp ~/anaconda/conda-bld/osx-64/arcgis-1.2.1-py35_1.tar.bz2 ___output/osx-64
cp ~/anaconda/conda-bld/osx-64/arcgis-1.2.1-py36_1.tar.bz2 ___output/osx-64

# to upload to anaconda - note uploads to the account logged in
# comment the lines below to turn this off.
anaconda upload ___output/linux-32/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/linux-32/arcgis-1.2.1-py35_1.tar.bz2
anaconda upload ___output/linux-64/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/linux-64/arcgis-1.2.1-py35_1.tar.bz2
anaconda upload ___output/osx-64/arcgis-1.2.1-py36_1.tar.bz2
anaconda upload ___output/osx-64/arcgis-1.2.1-py35_1.tar.bz2
# anaconda upload ___output/win-32/arcgis-1.2.0-py36_1.tar.bz2
# anaconda upload ___output/win-32/arcgis-1.2.0-py35_1.tar.bz2
# anaconda upload ___output/win-64/arcgis-1.2.0-py36_1.tar.bz2
# anaconda upload ___output/win-64/arcgis-1.2.0-py35_1.tar.bz2