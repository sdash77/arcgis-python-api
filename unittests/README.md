
# Introduction

Unittests to test the API. All code paths need to be tested. [Learn more about unittests](https://docs.python.org/2/library/unittest.html)


## Notes:

Test directory structure follows the code: /src/arcgis/* with subdirectories for each class or function.
* gis
* lyr
* tools
* viz

Only the following tests have been implemented:
* <root>\unittests\tools\geocoder\*.py

Use the tests as a starting point to expand and create new tests and fill in empty tests. [TO-DO]

At this time, the logic to loop over multiple portals in the root **unittest.ini** file has not been implemented. [TO-DO]

unittest.ini files in each sub-folder dont serve much purpose right now. However, they'll be useful in the future to help with test results.

## Running Tests

Set the portal URL, admin user, admin password in the root **unittest.ini** file

After installing the API, run either an individual test, or use the **run_test_cases.py** script to run all tests.


## Want to contribute?
See the wiki at https://github.com/ArcGIS/geosaurus/wiki for the project vision and guiding principles, areas needing help, and how to contribute.
