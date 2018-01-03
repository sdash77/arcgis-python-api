# Geosaurus Automation

This folder contains various Python scripts that can be used to automate the build, testing, documentation generation, and deployment of this Python API. Much of this functionality is used by the Continous Integration/Continous Release Jenkins server hosted internally at Esri at https://zion/ , although each of the scripts should be able to be run by themselves.

# Scripts

## jenkins\_entry\_point.py

This main script is called with 1 command line argument, specifying what sort of jenkins automated testing functionality you want to run (at the time of writing this, either the pull\_request job or the master job). This script will call functions in all the other scripts, doing various tasks from running the unit tests to building the documentation.

## automation\_setup.py/automation\_cleanup.py

Runs before and after all other python scripts called from jenkins\_entry\_point.py,

## build\_documentation.py

This script will run the correct documentation building functionality, depending on your host os, found in geosaurus/docs. It will place the results in geosaurus/automation/staging, either to be manipulated by you or used by another mechanism.

## build\_conda\_package.py

Runs the build script in ```./build/build.py```, creates conda packages and places it in staging/.

## publish\_results.py

Publishes generated conda packages to the ftp server at ftp://zion .

## run\_unit\_tests.py

Runs unit tests, places the results in the staging/ folder.

## staging/

The folder where all automation outputs are stored. Nothing in this folder will ever get tracked with git, and old files will get overwritten. If you would like to use these files in other places, you should move them before running any automation processes again.
