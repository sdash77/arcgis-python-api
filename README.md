# Vision

[ **A powerful Python library for spatial analysis, mapping and GIS** ](https://developers.arcgis.com/python/)

ArcGIS API for Python (codenamed Geosaurus) is a Python library for working with maps and geospatial data. It provides simple and efficient tools for sophisticated vector and raster analysis, geocoding, map making, routing and directions, as well as for organizing and managing a GIS with users, groups and information items. In addition to working with your own data, the library enables access to ready to use maps and curated geographic data from Esri and other autorotative sources. It also integrates well with the scientific Python ecosystem and includes rich support for Pandas and Jupyter notebook.

Geosaurus is a comprehensive GIS expressed in Python.  A GIS is a container of geographic information with associated:
* Configurable (schema driven) information model for all sorts of geographic datasets and information items
 * Features, maps, imagery, raster, observations, visualizations, analytic results, entity data, tabular datasets,…
* Intelligent container of information with data items organized by user, group, with metadata, with ratings/reputation,…
*    Functions for working with entire datasets
 *    Many wonderful things represented as functions against data organized into packages (used to be tools/toolboxes)
* APIs for constructing and drilling into the insides of datasets
 * Iterate over features, create new datasets and add data, etc.
 * Aka “I/O” libraries and ways to cast GIS data items into Python items (raster to SciPy, etc.)
* Items for understanding and visualizing data – not just data
 * Maps & Scenes
 * Pythonic mechanism for defining and working with these items

## Project details:
[Developer website](https://developers.arcgis.com/python/)

See the developer documentation and resources at https://developers.arcgis.com/python/

## Getting Started

### Installing

[Install guide for end users](https://developers.arcgis.com/python/guide/Install-and-set-up/)

Install steps for developers:

* Install Anaconda for Python 3.5 from https://www.continuum.io/downloads
* Download or clone this repo. ```git clone https://github.com/ArcGIS/geosaurus.git```
* ```conda env create --file environment.yml```
* Windows: ```activate geosaurus_dev_env```
* Linux/OSX: ```source activate geosaurus_dev_env```
* ```pip install -e ./src``` (for using latest source code)
* ```jupyter nbextension install --py --sys-prefix arcgis``` (for enabling the map widget for Jupyter notebook)
* ```jupyter nbextension enable --py --sys-prefix arcgis``` (to initialize the map widget in the browser every time the notebook loads)
* ```jupyter notebook``` (to start a jupyter notebook server)

### Build the Documentation

```bash
sphinx-apidoc -o apidoc -e -F -H arcgis -A Esri -V 0.1 -R 0.1 src
cd apidoc
make html
open _build/html/index.html
```

# Want to contribute?
See the wiki at https://github.com/ArcGIS/geosaurus/wiki for the project vision and guiding principles, areas needing help, and how to contribute.
