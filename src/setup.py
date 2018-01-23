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
from glob import glob
from subprocess import check_output, CalledProcessError, STDOUT
import logging
log = logging.getLogger()
here = path.abspath(path.dirname(__file__))

#Conda uses this setup file, but we want to supress some functionality
if "--conda-install-mode" in sys.argv:
    sys.argv.remove("--conda-install-mode")
    conda_install_mode = True
else:
    conda_install_mode = False

if conda_install_mode:
    #conda handles its own depedencies, so don't specify any pip-depedencies
    install_requires_depedencies = []
else:
    install_requires_depedencies = [
        'six',
        'notebook',
        'ipywidgets >=5.2.2,<7',
        'widgetsnbextension >=1.2.6,<3', 
        'pandas',
        'numpy',
        'pyshp',
        'matplotlib',
        'keyring',
        'winkerberos;platform_system=="Windows"']

def _post_install():
    """This function will run after 'pip install' finishes. It has 2 parts:
    1) activate the notebook map widget, equivalent of running these cmds:
        - jupyter nbextension install --py --sys-prefix arcgis
        - jupyter nbextension enable --py --sys-prefix arcgis
        - jupyter nbextension enable --py --sys-prefix widgetsnbextension
    2) If the O.S. is Mac OSX, run the OpenSSL workaround as described in
       this issue: https://bugs.python.org/issue28150, equivalent of running
       '/Applications/Python X.X/Install Certificates.command' cmd
    """
    if conda_install_mode:
	#Don't run any post installation methods for conda installs
        return

    # 1) activate the notebook map widget
    try:
        import notebook.nbextensions as nbext
        import arcgis
    except ImportError as e:
        log.exception("arcgis/notebook packages don't appear to be installed: "\
                      "map widget not activated, may not work. The rest of "\
                      "install is unaffected by this. Exception caught: ")
        return

    with _lower_log_level_to_debug(): #outputs success or failure to console
        nbext.install_nbextension_python("arcgis",
                                         sys_prefix = True, logger = log)
        nbext.enable_nbextension_python("arcgis",
                                         sys_prefix = True, logger = log)
        nbext.enable_nbextension_python("widgetsnbextension",
                                         sys_prefix = True, logger = log)

    # 2) If the OS is Mac OSX, run the OpenSSL workaround
    platform_is_osx = sys.platform == "darwin"
    if not platform_is_osx:
        return
    for potential_cert_script in glob("/Applications/Python*/*"):
        if "Install Certificates.command" in potential_cert_script:
            try:
                cmd_output = check_output(potential_cert_script,
                                          stderr=STDOUT)
                log.warn("OpenSSL workaround for OSX completed succesfully. "\
                         "See https://bugs.python.org/issue28150 for info. "\
                         "".format(cmd_output.decode("utf-8")))
            except CalledProcessError as e:
                log.warn("OpenSSL workaround for OSX did not complete "\
                         "successfully. This may or may not allow secure SSL "
                         "to work. See https://bugs.python.org/issue28150. "\
                         "Output: {}".format(e.output))

class _lower_log_level_to_debug:
    """Use with "with" syntax like "with _lower_log_to_debug():". Lowers
    the global root "log" object to DEBUG, resets it back to original after"""
    def __enter__(self):
        self.prev_logging_level = log.level
        log.setLevel(logging.DEBUG)

    def __exit__(self, type, value, traceback):
        log.setLevel(self.prev_logging_level)

# Each of these classes represent the different modes that pip install
# can go into, and what logic can be run after pip install finishes
class PostDevelopCommand(develop):
    """Post-installation logic to run for development mode"""
    def run(self):
        _post_install()
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation logic to run for installation mode"""
    def run(self):
        _post_install()
        #see http://bit.ly/2DfCXxx for why 'do_egg_install' instead of 'run'
        install.do_egg_install(self)

class PostEggInfoCommand(egg_info):
    """Post-installation logic to run for 'egg_info' mode"""
    def run(self):
        _post_install()
        egg_info.run(self)

# Get the long description from the README file
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

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
    install_requires = install_requires_depedencies,

    # These classes will execute code after 'pip install' finishes
    # In this case, it will activate the 'arcgis' ipywidget
    # See the top of this setup.py file
    cmdclass={'develop': PostDevelopCommand,
              'install': PostInstallCommand,
              'egg_info': PostEggInfoCommand}
    
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
