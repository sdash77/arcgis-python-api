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
[Developers website](https://developers.arcgis.com/python/)

See the developer documentation and resources at https://developers.arcgis.com/python/

## Getting Started (Installing)
If you are an end user, and would like to use the most recent publicly facing API, [follow these installation instructions](https://developers.arcgis.com/python/guide/Install-and-set-up/).

If you are an end user, and would like to use daily builds of this API, [follow these installation instructions](https://github.com/ArcGIS/geosaurus/wiki/Daily-Builds).

If you are a developer, follow these instructions:

* Install Anaconda for Python 3.X from https://www.continuum.io/downloads
* Download or clone this repo. ```git clone https://github.com/ArcGIS/geosaurus.git```
* ```conda env create --file environment.yml```
* Windows: ```activate geosaurus_dev_env```
* Linux/OSX: ```source activate geosaurus_dev_env```
* ```pip install -e ./src --no-deps``` (for using latest source code)
* ```jupyter notebook``` (to start a jupyter notebook server)

### The map widget isn't displaying
Try running these commands: 
* ```jupyter nbextension install --py --sys-prefix arcgis``` (for enabling the map widget for Jupyter notebook)
* ```jupyter nbextension enable --py --sys-prefix arcgis``` (to initialize the map widget in the browser every time the notebook loads)

## Build the Documentation

Go to the ```./docs/api_ref``` folder, and run the following commands:

Windows: ```.\make.bat html```
OSX/Linux: ```make html```

The results will be in ```./docs/build/html```. Open the ```index.html``` file.

## Navigating the Repository
* automation
    * This folder contains all of the code run for our C.I. system at http://zion/
* build
    * This folder contains build.py, the script used to generate all conda packages, or pip packages
    * This folder also contains all the conda config, like build/arcgis/meta.yaml, etc.
* docs
    * This folder contains the script and source for generating our API doc
    * This folder also contains the scripts to convert notebooks to html for the developer's website
* examples
    * Example notebooks
* src
    * This folder contains the pip config (setup.py, setup.cfg, etc.)
    * This folder also contains the actual source code of the API at src/arcgis
    * Note that src/changelog.txt only represents the changelog for pip releases
* unittests
    * This folder contains all of our unit tests, integration tests, etc.

# Want to contribute?
See the wiki at https://github.com/ArcGIS/geosaurus/wiki for the project vision and guiding principles, areas needing help, and how to contribute.
