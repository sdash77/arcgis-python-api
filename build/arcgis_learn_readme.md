# Building `arcgis_learn` package for conda

## Pre-requisites
Check readme.md for details

## Building Metapackage for ArcGIS Python API unreleased version (For testing internally)  
### Build the metapackage
    conda build -c pkgs/main -c esri -c http://zion/conda/1.8.5/ -c http://zion/conda/esri_channel_dev/ -c http://zion/conda/esri_requests/ arcgis_learn

### Copy or upload the artifacts to a local channel more details here [create-custom-channels](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/create-custom-channels.html)
    anaconda upload 'C:\ProgramData\Miniconda3\envs\build\conda-bld\win-64\arcgis_learn-1.8.5-py36_0.tar.bz2' -c http://zion/conda/arcgis_learn/
**Note: For now the upload does not work for http://zion/conda/arcgis_learn/ I am manually uploading it and indexing it.** 
    
### Install the Metapackage
    conda install -c esri -c http://zion/conda/1.8.5/ -c http://zion/conda/esri_channel_dev/ -c http://zion/conda/esri_requests/ -c http://zion/conda/arcgis_learn/ arcgis_learn=1.8.5 python=3.7

## Building Metapackage for ArcGIS Python API released version (For releasing publicly)
### Build the metapackage
    conda build -c pkgs/main -c esri arcgis_learn

## Installing Metapackage for ArcGIS Python API released version (For releasing publicly)
    conda install -c esri arcgis_learn
