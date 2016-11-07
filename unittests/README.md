# Unit tests framework for ArcGIS Python API

## Philosophy
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
		- check 
