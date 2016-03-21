# Vision
_**Python API to your Web GIS.**_

Web GIS is growing to include more out of the box analytical tools that work against data  items (feature layers, tables, images)  in your Web GIS. Having a powerful python api that helps publish data to my Web GIS, analyze it and visualize the results is of great interest.  Also managing my Web GIS as well as understanding whats going on with it (usage, etc).  Managing includes understanding dependencies between items, fixing up items, replication of items between portals, management of users, ... This project aims to provide this in a modern and easy to use Python API.

# Introduction

## Video demos

**A quick 10 minute demo of spatial analysis:**
* 01 Abridged Chennai Analysis 
* 02 Abridged Chennai Analysis  (at  https://esri.app.box.com/files/0/f/5801226685/ChennaiFloods)

**A longer version, with raster and vector geoanalytics included:**
* 01 Intro to Chennai Floods Analysis
* 02 What really caused the flooding
* 03 Creating a Raster product for analyzing Chennai Floods
* 04 The human impact and how GIS can help in relief efforts (at https://esri.app.box.com/files/0/f/5801226685/ChennaiFloods)

A series of smaller demos introducing the project and how it works (intro, gis administration, portal content management, visualization, geoprocessing, geometry, analysis):

* (01-09)*  at https://esri.app.box.com/files/0/f/5174399913/videos

## Documentation:

**Sample IPython notebooks:**
* http://dev04875.esri.com:8888/tree/

**API Reference as IPython Notebooks:**
* gis module: http://dev04875.esri.com:8888/notebooks/docs/gis%20module.ipynb
* viz module: http://dev04875.esri.com:8888/notebooks/docs/viz%20module.ipynb
* lyr module: http://dev04875.esri.com:8888/notebooks/docs/lyr%20module.ipynb

**API Reference as sphinx generated HTML documentation:**
* http://dev04875/ppyp/

## Project details:

**devtopia:**
* https://devtopia.esri.com/WebGIS/arcgis-python-api-to-webgis

**wiki:**
* http://mediawikidev.esri.com/index.php/Geosaurus/PortalPy++

**contacts:**
* Jay Theodore, Rohit Singh, Eva Mui

## Getting Started

### Build the Documentation

```bash
sphinx-apidoc -o apidoc -e -F -H arcgis -A Esri -V 0.1 -R 0.1 src
cd apidoc
make html
open _build/html/index.html
```

### Installing
_Requires Python3_

* Install Anaconda for Python 3.5 from https://www.continuum.io/downloads
* pip3 install -e . (for using latest source code)
   OR 
   pip install --extra-index-url=http://dev06999.esri.com:9000/ --trusted-host dev06999.esri.com arcgis (for a prebuilt pip package)
* python -m arcgis.install

### Running in iPython Notebook

Install [Jupyter](https://jupyter.readthedocs.org/en/latest/install.html)

```bash
pip3 install jupyter
jupyter-notebook
```

To test widgets open a new Python3 notebook in jupyter-notebook and issue following commands:
```
from arcgis.gis import *
gis = GIS()
gis.map()
```

# Want to contribute?
See the wiki at https://github.com/ArcGIS/geosaurus/wiki for the project vision and guiding principles, areas needing help, and how to contribute.
