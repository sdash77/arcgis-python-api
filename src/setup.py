"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
# To use a consistent encoding
from codecs import open
from os import path
import sys
import logging
log = logging.getLogger()

here = path.abspath(path.dirname(__file__))
ignore_post_install = False

def _install_enable_nbextensions_arcgis():
    """This function will run after 'pip install' finishes. It activates the 
    map widget for notebooks, equivalent of running the following commands:
        - jupyter nbextension install --py --sys-prefix arcgis
        - jupyter nbextension enable --py --sys-prefix arcgis
    """
    if ignore_post_install:
        return

    try:
        import notebook.nbextensions as nbext
        import arcgis
    except ImportError as e:
        log.exception("arcgis/notebook packages don't appear to be installed: "\
                      "map widget not activated, may not work. The rest of "\
                      "install is unaffected by this. Exception caught: ")
        return

    with _lower_log_level_to_debug(): #outputs success or failure to console
        nbext.install_nbextension_python("arcgis", logger = log)
        nbext.enable_nbextension_python("arcgis", logger = log)

class _lower_log_level_to_debug:
    """Use with "with" syntax like "with _lower_log_to_debug():". Lowers
    the global root "log" object to DEBUG, resets it back to original after"""
    def __enter__(self):
        self.prev_logging_level = log.level
        log.setLevel(logging.DEBUG)

    def __exit__(self, type, value, traceback):
        log.setLevel(self.prev_logging_level)

#Each of these classes represent the different modes that pip install
#can go into, and what logic can be run after pip install finishes
class PostDevelopCommand(develop):
    """Post-installation logic to run for development mode"""
    def run(self):
        develop.run(self)
        logging.info("Post-install logic in develop mode running")
        _install_enable_nbextensions_arcgis()

class PostInstallCommand(install):
    """Post-installation logic to run for installation mode"""
    def run(self):
        install.run(self)
        logging.info("Post-install logic in develop mode running")
        _install_enable_nbextensions_arcgis()

class PostEggInfoCommand(egg_info):
    """Post-installation logic to run for 'egg_info' mode"""
    def run(self):
        egg_info.run(self)
        logging.info("Post-install logic in egg mode running")
        _install_enable_nbextensions_arcgis()

# Get the long description from the README file
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

if "--ignore-post-install" in sys.argv:
    sys.argv.remove("--ignore-post-install")
    ignore_post_install = True

setup(
    name='arcgis',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.3.0',

    description='ArcGIS Python API',
    long_description='The ArcGIS API for Python lets ArcGIS Online and ArcGIS Enterprise users, analysts, developers and administrators script and automate tasks ranging from performing big data analysis to content management and administration of their web GIS. The API integrates well with the Jupyter Notebook and the SciPy stack and enables academics, data scientists, and GIS analysts to share programs and reproducible research with others.',

    # The project's main homepage.
    url='https://developers.arcgis.com/python/',

    # Author details
    author='Esri',
    author_email='python@esri.com',

    # Choose your license
    license='Esri Master License Agreement (MLA) - http://www.esri.com/LEGAL/pdfs/mla_e204_e300/english.pdf',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: Other/Proprietary License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='gis geographic spatial',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    packages=find_packages(),
    package_data={'arcgis': ['widgets/*.js',
                             'widgets/*.css',
                             'widgets/icons/*.png',
                             'widgets/requirejs/*.js']},
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'six',
        'pandas',
        'ipywidgets >=5.2.2,<7',
        'widgetsnbextension >=1.2.6,<3',
        'winkerberos;platform_system=="Windows"'],

    # These classes will execute code after 'pip install' finishes
    # In this case, it will activate the 'arcgis' ipywidget
    # See the top of this setup.py file
    cmdclass={'develop': PostDevelopCommand,
              'install': PostInstallCommand,
              'egg_info': PostEggInfoCommand},

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
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
)
