# About

This tool takes a directory of notebooks, and converts all notebooks into HTML files.

This tool is one part of many tools in that process from notebooks -> developers website. _It is recommended that you view this page for more information_ https://github.com/ArcGIS/geosaurus/wiki/Modifying-the-Developers-Website.

# How to use this tool.

## Dependencies
The following Python libraries are required. **Note**: Python API or ArcPy is not required as this script will export **without** executing the notebooks.

```
	conda install beautifulsoup4
	conda install nbconvert
```

## About this tool
Script needs the following command line parameters
 - path to the root level notebook folder
 - path to output folder to store the html file
 - whether of not to embed live nb link. (optional, defualt is False)
 - Whether or not to change all image paths to a certain prefix
 - What that image prefix should be

The script performs the following.
 - renames notebooks. Spaces and underscores are changed to '-'. Special char is removed. Filenames are made to lower case
 - export notebooks to basic HTML (no styling)
 - embeds title to the start of body tag (for SEO)
 - if option to embed 'Try it live' is enabled, embeds the code for those buttons.
 - Changes image paths

## Running the tool
Call from terminal. Type `-h` following the tool name to pull up the help

Call with command line args
```
λ python export_guide_samples_nb.py E:\temp\03-the-gis -o E:\temp\03-the-gis\outputs -e
Renaming folders
--------------------------------------------------------------------------
E:\temp\03-the-gis
E:\temp\03-the-gis\outputs
Renaming files
--------------------------------------------------------------------------
E:\temp\03-the-gis
E:\temp\03-the-gis\outputs
Exporting notebooks to html
--------------------------------------------------------------------------
E:\temp\03-the-gis
    Converting accessing-and-creating-content.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting accessing-and-managing-groups.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting accessing-and-managing-users.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting administering-your-gis.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting building-distributed-gis-through-collaborations.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting customizing-the-look-and-feel-of-your-gis.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting gis.admin-module.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting managing-your-content.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting managing-your-gis-servers.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting properties-of-your-gis.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting the-gis-module.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting using-the-gis.ipynb | exported  | made title  | made button  | wrote to disk.
    Converting working-with-different-authentication-schemes.ipynb | exported  | made title  | made button  | wrote to disk.
E:\temp\03-the-gis\outputs
```

# Dev notes: About Jupyter nbconvert 

### Convert to basic html
This is useful for embedding in websites.
`jupyter nbconvert <notebook> --to html --template basic`

### Convert multiple notebooks
```
jupyter nbconvert *.ipynb --to html --template basic
```
or you can spell out the names in the command line. You can also use a 	`mycfg.py`
