# CLI tool to manage content on AGOL and Enterprise

## Description

CLI tool to perform operations on content data files in both AGOL and Enterprise.
<br> Operations accepted :-
1. 'add' : for uploading content
2. 'update' : for updating content (thumbnail or item_properties or both) 
3. 'delete' : for deleting content
4. 'publish' : for publishing existing item 
5. 'add_publish' : for adding and publishing content in one go

### Workflow

1. User creates a CSV file containing information about content to be added, updated, published or add and publish in one go (Item Path, Item Properties, etc.).
2. User inputs authentication credentials and csv path in the CLI.
3. Content gets uploaded and progress of the operations are logged.

### Supported Authentication Types

1. Built In
2. PKI
3. IWA

#### Acceptable Inputs for Auth

|Auth Type|URL|Username|Password|Client Certificate|Client Secret/Key|Nothing|
|---|---|---|---|---|---|--|
|Built In|✔ (for Enterprise Users) |✔|✔|❌|❌|❌|
|PKI|✔ (for Enterprise Users) |❌|✔|✔|❌|❌|
|PKI|✔ (for Enterprise Users) |❌|❌|✔|✔|❌|
|IWA|✔|✔|✔|❌|❌|❌|
|IWA|✔|❌|❌|❌|❌|✔|

## How to Run?

Change directory to `"{FilePath}/Geosaurus/src/tools"`

### CLI Commands Overview

```cmd
usage: cli_tool.py [-h] [-fp] [-url] [-u] [-p] [-cert] [-secret]
                   [-b | -pki | -iwa] [-v]

Add data files

optional arguments:
  -h, --help            show this help message and exit
  -fp , --file_path     Path of input csv file containing list of Data Files
  -url , --url          URL for Enterprise Users
  -u , --user           Username for the GIS User
  -p , --password       Password for the GIS User
  -cert , --client_cert
                        Client Certificate for the GIS User
  -secret , --client_secret
                        Client Secret/Key for the GIS User
  -b, --built_in        Built In Account Auth
  -pki, --pki           PKI Auth
  -iwa, --iwa           IWA Auth
  -v, --verbose         To see the Traceback call on errors
```


### For Built In Auth

#### With Portal URL

```cmd
python cli_tool.py -fp [CSV_File_Path] -url [Portal_URL] -u [Username] -p [Password] -b
```
#### Without Portal URL

```cmd
python cli_tool.py -fp [CSV_File_Path] -u [Username] -p [Password] -b
```
### For PKI Auth with PFX Certificate and Password

```cmd
python cli_tool.py -fp [CSV_File_Path] -url [Portal_URL] -cert [Certificate_Path] -p [Password] -pki
```
### For PKI Auth with Certificate and Key Files

```cmd
python cli_tool.py -fp [CSV_File_Path] -cert [Certificate_Path] -secret[Key_File_Path] -pki
```
### For IWA with Username and Password

```cmd
python cli_tool.py -fp [CSV_File_Path] -url [Portal_URL] -u [Username] -p [Password] -iwa
```
### For IWA without Username and Password

```cmd
python cli_tool.py -fp [CSV_File_Path] -url [Portal_URL] -iwa
```

## Logging

### Log Type

In case of errors only the error messages and error codes are logged.
If the user wants to see the traceback call they can choose to do so by adding either of the following at the end of the command line argument.
```cmd
-v 
```
or
```cmd
--verbose
```

### Log File Destination

The tool logs all activity, by default the destination file is `sample.log` in the directory `"{FilePath}/Geosaurus/src/tools"`.

For a custom file name and path for the log file, you can change the log file path in `{FilePath}/Geosaurus/src/tools/cli_tool.py` at line 17 , refer to the code block below:-
```python
# For custom log_file path,refer to the line below
log_file_path = "<Enter Desired Log File Path and Comment the Line Below>"
log_file_path = "sample.log"
```

## Driver CSV description

<strong>The CSV should have the following headers:-</strong>
1. 'operation' : Required STRING indicating name of the operation to be performed
<br>Acceptable inputs - <br>
    1. 'add' : for uploading content <strong>[data required and item_id optional]</strong>
    2. 'update' : for updating content (thumbnail or item_properties or both) <strong>[item_id required]</strong>
    3. 'delete' : for deleting content <strong>[item_id required]</strong>
    4. 'publish' : for publishing existing item <strong>[item_id required]</strong>
    5. 'add_publish' : for adding and publishing content in one go <strong>[data required and item_id optional]</strong>
2. 'data' : Optional STRING indicating the local file path or URL of the content data file (if adding or adding and publishing)
3. 'thumbnail' : Optional STRING indicating the local file path or URL of the content thumbnail (if adding or adding and publishing)
4. 'owner' : Optional String
5. 'metadata' : Optional String
6. 'folder' : Optional String
7. 'item_id' : Optional String indicating item id for the content
8. 'item_properties' : Optional String dictionary indicating item properties for the content

