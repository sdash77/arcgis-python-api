# About

All of the content you see at https://developers.arcgis.com/python/ comes from either the arcgis-python-api notebooks repository or the arcgis-for-developers repository. Our notebooks are the "source of truth" on much of our documentation, and we convert those notebooks to HTML in a format the developers website can understand. See https://github.com/ArcGIS/geosaurus/wiki/Modifying-the-Developers-Website for the complete workflow

# notebooks\_to\_dev\_site.py

This script converts all notebooks in the arcgis-python-api repository to html pages in a format that the arcgis-for-developers repository understands, and it will copy the html files to the specified arcgis-for-developers repo. Use it like this:

```python notebooks_to_dev_site.py -n /path/to/arcgis-python-api -d /path/to/arcgis-for-developers```

See https://github.com/ArcGIS/geosaurus/wiki/Modifying-the-Developers-Website#section-c-modifying-the-developers-website-locally-before-pushing-to-origin for how to use this script. That wiki page also describes how this system integrates with the C.I. system at http://zion/

# Placing symlinks/repositories in this directory

This `.gitignore' file specifies that this directory won't track anything besides this README and the python script. You can place anything else in this directory and git won't track it.
