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
		- Portal IWA with some cred (should be ignored)
		- Portal PKI with key and cert file
		- Portal with bad cert and check `verify_cert` works
	- gis.datastores()  returns a list for each known server
		- try for AGO and recieve length 0 instead of traceback
	- gis.properties -- export as dict and perform comparison against a known dict

### DatastoreManager class
Set up class to enumerate existing state of data store. 
Tear down class to reset back to the set up state. Send a pull request after building a `remove` method as its required for the tear down. 
Set up method to find if data location can be pinged
Tear down method: none

	- config getter -- bool
	- config setter -- check with config getter. Reset on teardown
	- add_folder()
		- shared folder valid. Assert with search() and get()
		- replicated folder valid. Assert with search() and get()
		- add existing folder. Assert with search() no duplicates created
	- add_bigdata()
		- valid big data folder. Assert with search() and get()
		- duplicate big data folder. Assert with search() no duplicates
	- add_database()
		- a valid conn string for shared db. Assert with search() and get()
		- a valid conn string for client & server. Assert with search() and get()
	- add()
		- fire this with a known dict such as for a shared folder and validate with search()
	- get() 
		- valid cases is tested as part of add functions
		- invalid case returns None
	- search()
		- valid cases tested with add functions
		- test for optional parameters
	- validate()
		- call after adding a valid shared folder : True case
		- call after adding an invalid shared folder: False case

### ContentManager class
Tests for adding, deleting, searching content and folders. The set up and tear down fixtures will be used heavily to reset the portal back to initial state. Test cases:

	- setUpClass - create GIS connection, test asset location,
	- setUp - delete old outputs
	- add
		- empty data (just an item)
		- csv
		- .sd
		- .gdb zip
		- .shp zip
		- data = http url to a file
		- item properties
			- snippet
			- tags as list
			- tags as comma sep string
		- owner
			- user obj
			- string
			- empty
		- thumbnail path to png or url to .png file
		- metadata - string - path or url to metadata.xml file
		- folder
			- existing
			- new
		- failing case to return none (file not found)
	- _is_shapefile - logic to extract a zip to find if there is a file with .shp extension
	- create_service - can only publish a HFS
		- Feature service
		- name in i18n
		- service_desctiption in i18n
		- max_record_count and validate
		- capabilities - empty
		- capabilities - with value
		- description
		- wkid - default
		- wkid - custom
		- create_params - custom
		- service_type - bug should be compulsory parameter
		- owner - empty
		- owner - custom
		- folder - empty
		- folder - existing
		- None upon failure
		- Initial extent always set to a default
	- get
		- valid entry
		- invalid should return None
	- search - reminder to self: if query does not return something, it could be the portal framework.
		- query
			- empty
		- owner
		- item_type : feature service, sd file (we need a bank of 	items for search to work)
			- web map, web scene, feature layer, gp tool, image service, layer, desktop application, project package, word doc, pdf, csv, sd, kml, lpk, mpk, spk, lpkx, mpkx, ppkx
		- sort_field: type, uploaded
		- sort_order:
		- max_items:
		- outside_org: for AGO only
		- return is a list
		- bad entries for any of the parameters should always return empty list
	- create_folder
		- valid folder name in i18n and no owner
		- valid name for diff User obj
		- valid name for diff Username string
		- '/' for name
		- valid name for non existing onwer
		- invalid name ?
		- exsiting folder should return None
	- delete_folder
		- '/' should return False
		- valid name in i18n and owner none
		- valid name and User obj
		- valid name and User string
		- invalid name and owner none
	- is_service_name_available
		- existing name and type
		- existing name invalid type should return False
		- invalid name should return False

## ini files
unittest.ini file contents

	- At module level
		- conn credentials to AGO

## Utilities
dino_utils:

	- Statefinder: get initial state of a system. Such as
		- user list
		- groups list
		- items list
		- datastore items
	- PreCondition checks
		- check OS
		- check arcpy import
		- check python version
		- check api can be imported
	- ValidationUtils
		- check item exists
		- check user exists
    - PortalUtils
        - search, delete content
        - populate portal with users, groups, folders, content

# Jenkins settings
A Jenkins server running on a VM performs the continuous integration testing. Details below:

    - Server: teton.esri.com:8080 [need to be on VPN to access this machine]
    - URL: [http://teton.esri.com:8080/jenkins](http://teton.esri.com:8080/jenkins)
    - credentials: contact Atma
    - Jenkins job: [run_master_tests](http://teton:8080/jenkins/job/run_master_tests/lastCompletedBuild/testReport/)
        - This job has a sub job called `pull_geosaurus_master` which 
        polls the github repo and pull changes every 5 minutes
        - If any changes, the local clone is updated and the `run_master_tests` is triggered.
        - As the build job runs and tests are executed, status messages 
        are posted to `#dino_tests` channel of [geosaurus.slack.com](http://geosaurus.slack.com)
    - Future plans include building a conda package for each checkin and 
    spinning up a docker container, installing the package and testing it.
    
In case teton.esri.com had to be restarted, you can resume Jenkins by running `C:\work\tomcat9\bin\startup.bat`

# Testing pattern
The `PortalUtils` creates two set of users. Use set1 content in test asset location
to populate the portal. Use set2 content in the tests on user1. Re assign this to user2
or create this content for user2 when applicable.