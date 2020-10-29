# Documenting Geosaurus using Sphinx and Read The Docs theme

**Toc**
<!-- MarkdownTOC -->

- [Set up](#set-up)
- [Generate API Reference](#generate-api-reference)
- [Quickstart](#quickstart)
- [Customizing conf.py](#customizing-confpy)
- [Building the help](#building-the-help)
  - [Customizing the toctree](#customizing-the-toctree)
    - [index.rst](#indexrst)
    - [additional module rst files](#additional-module-rst-files)
    - [arcgis.gis.toc.rst and the remaining such module files](#arcgisgistocrst-and-the-remaining-such-module-files)
- [On-going doc updates](#on-going-doc-updates)

<!-- /MarkdownTOC -->

## On-going doc updates
All Sphinx and theme related configurations for the Geosaurus repo are completed and included in the repository itself. If all you want to do is edit/add API ref and build it to view the HTML files, then you can accomplish it using the single step mentioned below:

 - From the Command Prompt, simply run `make html` from the `docs/api-ref` folder to re-build the API and export it as `html` and index it.
 
 Do this step regularly throughout the editing session to verify the translation of the Python docstrings to `html`. You might see several warnings. As long as you do not see errors, you are fine. We will slowly address those warnings.

## What to do during a release:
During a release, edit the `copyright`, `version`, `release` variables with the new year and new version number. Next, edit the `versions` List (around line `360`) to include the current version into this list of older versions.

Next, build the API ref as explained earlier and ensure the version number, copyright year and older version picker are all updated appropriately.

**Note:**  The initial `rst` files are built by running `sphinx-apidoc -f -o source ../src/arcgis` from `docs/api-ref` folder. This creates / updates the `rst` files, but generally is not part of the on-going documentation process.  These `rst` files are gained locally by pulling the latest repo.  Any new modules that get created will require an `rst` file be created, also.

----------------------------
> **⚠ WARNING: Read this first.**  
> This wiki walks through the steps involved in setting up Sphinx for a new Python
> project. All the configurations for Geosaurus have already been completed. To simply
> update and build the API ref into HTML files, skip to the section on '[On-going doc updates](#on-going-doc-updates)'
----------------------------

## One-time set up notes:
In your dev environment (conda) install sphinx
```
conda install sphinx
pip install sphinx-rtd-theme
```

Then make a `docs` dir next to the `src` directory. The `docs` will house the build files for documentation and also the built `html` pages in RTD theme. Then

```
cd docs
```


### Generate API Reference

If you simply want to generate the API reference, all you need to do is:
```
cd docs\api_ref
make html
```
The doc would be generated in `docs/api_ref/build/html` folder.

The notes below talk about the process to get to this point (valid for a new project) and can be ignored for the Geosaurus project as all steps have already been run once to generate the config.

### Sphinx Quickstart command
Execute `sphinx-quickstart` this fires a set of questions and creates the `conf.py` which contains the config settings and a default `index.rst` file containing the skeleton TOC for help.

```
sphinx-quickstart
```
say yes to
  - separate source and build dir
  - project name: `arcgis`
  - Author: `Esri`
  - versions: `0.3` or `1.0` as appropriate
  - audodoc: `yes`
  - create make file: `yes`
  - create windows cmd line: `yes`

**Note**: The quickstart is a one-time process. Since this is done for Geosaurus, you don't have to repeat it.

### Customizing conf.py
Update the `conf.py` with the following values. This applies primarily to getting the RTD theme. Search the file, most of these would be commented out and you need to uncomment and fill with correct values

```PYTHON
import sphinx_rtd_theme

# Add the source code to sys path. Sphinx autodoc will try to import the source 
# during the build process
sys.path.insert(0,'../../src/')

html_theme = 'sphinx_rtd_theme'

html_theme_options = {'collapse_navigation': False,
    'display_version': True}

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
```

#### Editing the bottom left corner of the left pane
The left pane contains the ToC. To add the version picker / options pull out, we override the template and store it in `docs/api_ref/source/_templates/versions.html` file. We also edit `/docs/api_ref/source/conf.py` by listing all the versions we need to show in the version picker and the URLs to each. Currently, the URLs are relative and folder names are same as the 3 decimal version number (such as `1.8.1`, `1.0.0`). 

**Note**: Similar to quickstart, this is a one-time step and is done for Geosaurus project. This step need not be repeated even on new computers.

### Building the help the very first time
Sphinx builds doc in a 2 step process - it first builds the `rst` (ReStyle Text) files and stores them in the `source` folder. These `rst` files form the outline for the TOC and actual help. The second step is triggered manually which converts the `rst` to an output format, which in our case is `html`. During the 2nd step, sphinx will also index the contents for the search to work.

Thus, after customizing `conf.py`, you need to build the help before proceeding to the next steps.

In your terminal from within the `docs` dir:

```
sphinx-apidoc -f -o source ../src/arcgis
```
the `-f` will force to rebuild all files. This process creates the `index.rst`, `arcgis.rst` and `modules.rst` files.

### Customizing the toctree
#### index.rst
Start with `index.rst`. This file should contian the `modules` under `arcgis` package. Nothing more as shown below:

```
API Reference for the ArcGIS Python API
=======================================

Contents:

.. toctree::
   :maxdepth: 3
   :caption: arcgis

   arcgis.gis.toc
   arcgis.env
   arcgis.features.toc
   arcgis.raster.toc
   arcgis.network.toc
   arcgis.geoanalytics.toc
   arcgis.geocoding
   ....

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
```
I pulled out the `* :ref:`search`` since search was part of the theme.

#### Additional module rst files
We will break up the `arcgis.rst` autogenerated and create additional files for each module as
  - arcgis.gis.toc.rst
  - arcgis.features.rst
  - arcgis.raster.rst
  - arcgis.network.rst
  - arcgis.geoanalytics.rst
  ...

Thus, each sub-module gets its own `.rst` file.

#### `arcgis.gis.toc.rst` and the remaining such module files
Edit this file and make use of `audomodule` and `autoclass` keywords to limit what is shown and what is nested. This took me many experiments to figure out. Consider this part as having full control over what appears in the doc but while still using autodo to build it. You are only telling autodoc what to include (or not) and where to put what. The autodoc does the rest. Each of the files shoud look like the example below:

```
arcgis.gis module
=================

arcgis.gis.GIS
--------------
.. autoclass:: arcgis.gis.GIS
    :members:
    :undoc-members:

arcgis.gis.ContentManager
-------------------------
.. autoclass:: arcgis.gis.ContentManager
    :members:
    :undoc-members:

arcgis.gis.Item
---------------
.. autoclass:: arcgis.gis.Item
    :members:
    :undoc-members:

-----------------
and so on
-----------------
```

Note, here I left out the 'rot13' function or any other utility method we have in source code that we dont want the autodoc to pick up. Also note, you can control the order of the doc. Here I have placed `Item` class next to `ContentManager`.
