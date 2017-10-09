# Building `arcgis` package

## Pre-requisites
You need `conda-build` package installed. This can only be installed in the `root` environment. Hence run the following from terminal to activate your root and install the package

	source deactivate
	conda install conda-build

To upload the package to [anaconda.org](https://anaconda.org) you need `anaconda-client` and a free account. Install this in root env
	
	conda install anaconda-client
	anaconda login

## Build process
Here is the [api doc for conda build](https://conda.io/docs/commands/build/conda-build.html) with all its optional parameters and here is the [tutorial to build pacakges](https://conda.io/docs/building/build.html). My [detailed wiki here](https://devtopia.esri.com/atma6951/kiwi/wiki/Building-Conda-Packages)

### Updating version number and dependencies
The version number needs to be updated in the following files

 - conda recipe file `geosaurus/build/arcgis/meta.yaml` - If necessary, update the package's dependencies (if we added any)
 - `src/arcgis/__init__.py` this file reports the version when used as `arcgis.__version__`
 - `src/arcgis/copyright.txt` for legal purposes
 - `src/setup.py` for non traditional installers

Similarly, update the build scripts `geosaurus/build/buildarcgis.sh` such that version number of the package is updated in the file name for the `conda convert` command.

### Building
From the `geosaurus/build/` folder run the `buildarcgis` script - either the .sh or .bat depending on your OS. The `.bat` file accepts the version number as command line parameter.
	
	buildarcgis.bat 1.2.5

This runs the build, post-link, validation steps and creates the files in a local dir. Then the script calls `conda convert` which will convert and copy to `___output` folder.

### Upload to anaconda org
To run this either, run the `geosaurus/build/upload.bat` or `geosaurus/build/upload.sh`. You can also uncomment the upload part from the `geosaurus/build/buildarcgis.sh` or `buildarcgis.bat` script to enable uploading after building.

**Note**, upload will use the currently logged in user (`anaconda login` command)