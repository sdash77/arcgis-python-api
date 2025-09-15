"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup
from setuptools import find_packages
from setuptools.dist import Distribution
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
from setuptools.command.egg_info import egg_info as _egg_info

# To use a consistent encoding
from codecs import open
from os import environ, path
import sys
from glob import glob
from subprocess import check_output, CalledProcessError, STDOUT
import logging
import site

import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)


here = path.abspath(path.dirname(__file__))


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""

    def has_ext_modules(foo):
        return True


def _get_rel_site_packages_dir():
    for sitepackages in site.getsitepackages():
        try:
            res = "lib" + sitepackages.split("lib")[1] + "/arcgis/gis/_impl"
            if res:
                return res
        except Exception:
            pass


dependencies = [
    "pillow",
    "urllib3>=2.1.0,<3",
    "cachetools",
    "lxml",
    "cryptography",
    "pandas >=2.0.0,<2.4.0",
    "numpy >=2.2.0,<3",
    "matplotlib",
    "keyring >=23.3.0",
    "pylerc",
    "ujson >=3",
    "truststore>=0.10.0",
    'pywin32 >=223;platform_system=="Windows"',
    "geomet >=1.0.0",
    "requests >=2.32.3,<3",
    "requests-oauthlib",
    "requests_toolbelt",
    "pyspnego >=0.8.0",
    "dask[dataframe] >=2024.12.1,<2025.3",
    "matplotlib-inline",
    "pyarrow >=17,<21",
    "puremagic >=1.15,<2",
    "pydantic >=2.8.2, <3",
    "networkx >=3.3, <4",
    "websocket-client >=1.2.3, <2.0.0",
]


def _post_install():
    """stub for post-installation logic when installing source distribution"""
    return


# Each of these classes represent the different modes that pip install
# can go into, and what logic can be run after pip install finishes
class develop(_develop):
    """Post-installation logic to run for development mode"""

    def run(self):
        self.execute(_post_install, (), msg="Running post-install...")
        super().run()


class install(_install):
    """Post-installation logic to run for installation mode"""

    def run(self):
        self.execute(_post_install, (), msg="Running post-install...")
        super().run()


class bdist_wheel(_bdist_wheel):
    """Configures bdist_wheel to be platform-agostic"""

    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = True


class egg_info(_egg_info):
    """Post-installation logic to run for 'egg_info' mode"""

    def run(self):
        self.execute(_post_install, (), msg="Running post-install...")
        super().run()


# Read the description.md file
try:
    description_md_file = open("pypi_long_description.md", "r")
    long_description = description_md_file.read()
    description_md_file.close()
except:
    long_description = "ArcGIS API for Python"


def get_version():
    """gets the version from environment variable or sets via manually setting"""
    ARCGIS_PYTHON_API_VERSION = "2.4.2"
    return environ.get("ARCGIS_PYTHON_API_VERSION") or ARCGIS_PYTHON_API_VERSION


kwargs = {
    "name": "arcgis",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    "version": get_version(),
    "description": "ArcGIS API for Python",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    # The project's main homepage.
    "url": "https://developers.arcgis.com/python/",
    # Author details
    "author": "Esri",
    "author_email": "python@esri.com",
    # Choose your license
    "license": "Esri Master License Agreement (MLA) - http://www.esri.com/LEGAL/pdfs/mla_e204_e300/english.pdf",
    "platforms": ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    "classifiers": [
        # How mature is this project? Common values are
        "Development Status :: 5 - Production/Stable",
        # Topics
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        # OS
        "Operating System :: OS Independent",
        # Pick your license as you wish (should match "license" above)
        "License :: Other/Proprietary License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    # What does your project relate to?
    "keywords": "gis arcgis geographic spatial spatial-data "
    "spatial-data-analysis spatial-analysis data-science maps "
    "mapping web-mapping python native-development",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    "packages": find_packages(),
    "python_requires": ">=3.10, <3.14",
    "include_package_data": True,
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # `setup_dependencies` are all dependencies that need to be in the env
    # BEFORE setup() is called. `install_dependencies` are dependencies
    # that can be put in the env AFTER setup() is finished. See bottom of this
    # file, any unhandled exception will clear `setup_requires` and try again
    # It was thought `setup_requires` needed `notebook` and other deps to
    # activate the map widget, but it caused build errors on windows with
    # required VS C++ distrib (even for --no-deps). See geosaurus/issues/964
    "install_requires": dependencies,
    "setup_requires": dependencies,
    # These classes will execute code after 'pip install' finishes
    # In this case, it will activate the 'arcgis' ipywidget
    # See the top of this setup.py file
    "cmdclass": {
        "develop": develop,
        "install": install,
        "egg_info": egg_info,
        "bdist_wheel": bdist_wheel,
    },
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    "extras_require": {
        "gp": ["dill"],
        "gdal": ["gdal >=3.9.2, <4"],
        "kerberos": [
            "requests-kerberos",
            "requests-gssapi",
        ],
    },
    "distclass": BinaryDistribution,
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },
    "package_data": {
        "arcgis": [
            "apps/workforce/_store/resources/default-project-thumbnail.png",
            "gis/_impl/*.pyd",
            "gis/_impl/*.so",
            "graph/_decoder/**/*.pyd",
            "graph/_decoder/**/*.so",
            "learn/*.dll",
            "learn/*.so",
            "learn/_mmdetection_config/*.py",
            "learn/_mmdetection_config/**/*.py",
            "learn/_mmdetection_config/**/**/*.py",
            "learn/_mmseg_config/*.py",
            "learn/_tracking/*.pyd",
            "learn/_tracking/*.dll",
            "raster/*.dll",
            "raster/*.so",
        ],
    },
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
}

try:
    setup(**kwargs)
except Exception:
    log.exception(
        "Exception encountered when attempting to install: Setting "
        "`setup_requires` arg to `[]` and trying again. Exception:\n-----\n"
    )
    kwargs["setup_requires"] = []
    setup(**kwargs)
