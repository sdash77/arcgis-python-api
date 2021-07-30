# API Ref style guide
This document aims to show how to author doc-strings which get converted to Python API's api-ref documents.

-- to be filled --


## Customizing Table of Contents with subjective groupings
By default, the sphinx engine lays out all the classes and static functions at the root level of a module. Usually the 
members are sorted alphabetically. However, for a large API, this becomes tedius to navigate or to quickly understand
the layout of that module's members. 

A solution is to customize the `toctree` by introducing subjective groupings. In essence, this overwrites what sphinx
makes by default and puts responsibility on the team **to add new members manually** to the `toc.rst`. See 
https://github.com/ArcGIS/geosaurus/pull/6844/ for pictures and the API ref for `mapping` module once that PR is merged
for examples.

### Making subjective groups
By default, the sphinx toctree looks like this:

```rst
arcgis.mapping module
=================

.. automodule:: arcgis.mapping

WebMap
-----------------
.. autoclass:: arcgis.mapping.WebMap
    :members:
    :undoc-members:
    :show-inheritance:

OfflineMapAreaManager
-----------------------
.. autoclass:: arcgis.mapping.OfflineMapAreaManager
    :members:
    :undoc-members:
    :show-inheritance:
```
You can change this to:
```rst
arcgis.mapping module
=================

.. automodule:: arcgis.mapping

Working with 2D Maps
--------------------
WebMap
^^^^^^
.. autoclass:: arcgis.mapping.WebMap
    :members:
    :undoc-members:
    :show-inheritance:

OfflineMapAreaManager
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: arcgis.mapping.OfflineMapAreaManager
    :members:
    :undoc-members:
    :show-inheritance:
```
which will group `WebMap`, `OfflineMapAreaManager` and the rest under the group `Working with 2D Maps`. The key is to 
immediately follow a heading with dashed underlines (`Working...Maps` in this case) with another sub-heading with carrot
underlines (`Webmap` in this case). Sphinx will break this group when it encounters another heading with dashed underlines.

As you know sphinx is finicky and this, like the rest would require a bit of tiral and error to ensure the char spacing,
line spacing is not interfering with something sphinx expects.

### Customizing submodules in subjective groups
The example above shows how to group classes and functions. This section shows how to customize the group names for sub-modules.
By default, sphinx calls this as `Submodules` and the toctree looks like below:

```rst
Submodules
--------------
.. toctree::
   :maxdepth: 3

   arcgis.mapping.ogc
   arcgis.mapping.forms
```
You can customize this to look like below:
```rst
Working with OGC layers
-----------------------
arcgis.mapping.ogc
^^^^^^^^^^^^^^^^^^
.. toctree::
   :maxdepth: 3

   arcgis.mapping.ogc

Working with Map Forms
----------------------
arcgis.mapping.forms
^^^^^^^^^^^^^^^^^^^^
.. toctree::
   :maxdepth: 3

   arcgis.mapping.forms
```
You simply repeat the `..toctree::` directive for each item under your group **and in the corresponding toctrees of 
submodules**, you need to **remove** the following:
```rst
arcgis.mapping.forms module
===================

.. automodule:: arcgis.mapping.forms
```
You can, in theory, recursively customize the toctree of submodules to have their own groupings. But I have not tried this
yet.