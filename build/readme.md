# Building `arcgis` package for conda

## Pre-requisites
You need `conda-build` package installed. This can only be installed in the `root` environment. Hence run the following from terminal to activate your root and install the package

	source deactivate
	conda install conda-build

To upload the package to [anaconda.org](https://anaconda.org) you need `anaconda-client` and a free account. Install this in root env
	
	conda install anaconda-client
	anaconda login

## Build process
Run build.py to generate conda packages in the output/ folder. At the moment, you can only build windows conda packages from a windows machine, and you can only build osx/linux conda packages from a unix machine.

build.py can also generate the .tar.gz tarball for uploading to a PyPI server. Use the --pip flag.

Examples:
* 'python build.py --help' to print out the help text
* 'python build.py' for default build behavior
* 'python build.py -p 3.5 3.6 -o osx-64 linux-32' for building both py3.5 and py3.6 for both osx-64 and linux-32
* 'python build.py --all' for building for all platforms and all python versions supported by this system for conda pkgs, as well as building the pip pakcage
* 'python build.py --upload' for default build behavior, plus upload any results to the anaconda cloud
* 'python build.py --pip' for building the .tar.gz pip package

# pip and PyPI servers

http://zion has a PyPI server running at it, see the wiki page on daily builds for more information. If you would like to upload the package to the official PyPI server, see the following link: http://peterdowns.com/posts/first-time-with-pypi.html David Vitale manages this process for uploading to both our internal and the official PyPI servers, contact him for more info.

### Updating version number and dependencies
The version number needs to be updated in the following files

 - conda recipe file `geosaurus/build/arcgis/meta.yaml` - If necessary, update the package's dependencies (if we added any)
 - `src/arcgis/__init__.py` this file reports the version when used as `arcgis.__version__`
 - `src/arcgis/copyright.txt` for legal purposes
 - `src/setup.py` for non traditional installers

Similarly, update the build scripts `geosaurus/build/buildarcgis.sh` such that version number of the package is updated in the file name for the `conda convert` command.

### Misc
Here is the [api doc for conda build](https://conda.io/docs/commands/build/conda-build.html) with all its optional parameters and here is the [tutorial to build pacakges](https://conda.io/docs/building/build.html). My [detailed wiki here](https://devtopia.esri.com/atma6951/kiwi/wiki/Building-Conda-Packages)

