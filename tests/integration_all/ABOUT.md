# Unit tests framework for ArcGIS Python API

<!-- MarkdownTOC -->

- [Philosophy](#philosophy)
- [Architecture](#architecture)
	- [SetUp Module](#setup-module)
	- [GIS Module](#gis-module)
		- [GIS class](#gis-class)
		- [DatastoreManager class](#datastoremanager-class)
		- [ContentManager class](#contentmanager-class)
	- [ini files](#ini-files)
	- [Utilities](#utilities)
- [Jenkins settings](#jenkins-settings)
- [Testing pattern](#testing-pattern)

<!-- /MarkdownTOC -->

# Philosophy
The purpose of these unit tests is to verify the various functions and 
capabilities of the API work and don't regress. It is **not** to verify 
the ArcGIS Platform works. For instance, the unit test method called 
`DatastoreManager.add_folder()` is to verify that a folder gets added to
the data store. It is not to verify what happens if an invalid path is 
entered or if the server promptly checks if it has read access to the UNC
path. Such checks must be performed at the unit tests meant for data store
code base. This is a concious decision since it allows the author to
get an accurate picture of the API health. If the tests also check 
for ArcGIS Server health, a regression in data store code base can result
in a test failure for the API, all the while, the API fires the right REST API calls and parameters.

# Architecture
## SetUp Module

## GIS Module
### GIS class
	- setup class
		- ensures test can ping url
	- teardown class
		- call the logout method?
	- setup method
		- none
	- teardown method
		- none
	- create connection for
		- AGO with correct credentials
		- AGO with wrong credentials
		- Portal with correct
		- Portal with wrong
		- Portal IWA with no cred

# Introduction

Unittests to test the API. All code paths need to be tested. [Learn more about unittests](https://docs.python.org/2/library/unittest.html)


## Notes:

Test directory structure follows the code: `/src/arcgis/*` with subdirectories for each class or function.
- [ ] gis
  - [ ] content manager
  - [ ] group
  - [ ] group manager
    - [ ] ![Progress](http://progressed.io/bar/90)
  - [ ] item
  - [ ] tools
  - [ ] user
  - [ ] usermanager
- [ ] lyr
  - [ ] ![Progress](http://progressed.io/bar/0)
- [ ] viz
  - [ ] ![Progress](http://progressed.io/bar/0)
- [ ] tools
  - [x] geocoder  ![Progress](http://progressed.io/bar/50)
  - [ ] geometry
 

![Progress](http://progressed.io/bar/01) Use the **geocoder** tests as a starting point to expand and create new tests and fill in empty tests. 

![Progress](http://progressed.io/bar/0) At this time, the logic to loop over multiple portals in the root **unittest.ini** file has not been implemented.

unittest.ini files in each sub-folder dont serve much purpose right now. However, they'll be useful in the future to help with test results.

## Running Tests

Set the portal URL, admin user, admin password in the root **unittest.ini** file

After installing the API, run either an individual test, or use the **run_test_cases.py** script to run all tests.


## Want to contribute?
See the wiki at https://github.com/ArcGIS/geosaurus/wiki for the project vision and guiding principles, areas needing help, and how to contribute.
