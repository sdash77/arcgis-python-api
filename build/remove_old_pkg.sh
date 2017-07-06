#!/bin/bash

logged_in_user='atmamani'
ver_to_remove='1.2.0'
ver_to_build='1.2.0'
# logged_in_user = 'geonuma'

anaconda remove -f $logged_in_user/arcgis/1.2.0/osx-64/arcgis-1.2.0-py36_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/osx-64/arcgis-1.2.0-py35_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-64/arcgis-1.2.0-py36_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-64/arcgis-1.2.0-py35_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-32/arcgis-1.2.0-py36_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/linux-32/arcgis-1.2.0-py35_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/win-64/arcgis-1.2.0-py36_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/win-64/arcgis-1.2.0-py35_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/win-32/arcgis-1.2.0-py36_1.tar.bz2
anaconda remove -f $logged_in_user/arcgis/1.2.0/win-32/arcgis-1.2.0-py35_1.tar.bz2