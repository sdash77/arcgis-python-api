# API Ref style guide
This document serves as a guideline for contributing to the API Reference
documentation for the ArcGIS API for Python. It includes a brief overview
of setting up a conda environment and a workflow for managing Git daily 
to build the API Reference locally. It also includes tips and advice for
efficient work and debugging, and syntax to use in Python docstrings to
add code emphasis and hyperlinks to other portions of the api reference.

## Set up the `conda` environment
1. Clone the geosaurus repo from _https://github.com/arcgis/geosaurus_
2. Navigate to the geosaurus directory:
  `cd path_to_newly_cloned_repo\geosaurus`
3. Create the default environment from configuration file in the repo:
  ```python
  conda env create -f environment.yml
  ```
  * **Note:** Anaconda or Miniconda must be installed on your system to 
  provide access to the `conda` utility. Add the pathway to your installation 
  to run the command above without having to navigate to the install
  directory.
  * The `environment.yml` file in the geosaurus repo contains a list 
  of all dependencies for the API for Python and instructs conda to create
  an environment named `geosaurus_dev_env` and install all the dependencies
  within that environment.
4. Activate the environment:
```python
conda activate geosaurus_dev_env
```
5. Navigate to the API Reference directory in the repo:
`cd docs/api_ref`
6. Build the API Reference locally:
`make html` 
7. Open your file system's browser and navigate to the 
_geosaurus/docs/api_ref/build/html_ directory. Locate the _index.html_ file 
and open it in the web browswer of your choice. You will have a locally
rendered API for Python Reference for you to test out changes you make
to docstrings in your local branch.

## Sample Workflow for editing API Reference

Managing `git` can be confusing, but a daily workflow to
establish consistent code practices will help avoid merge conflicts when
pushing upstream.

Use the following steps to maintain an updated working branch. Make sure
you have activated the `geosaurus_dev_env` so you have access to
the `sphinx` software and `sphinx-rtd-theme` used the API for Python 
api reference:
```bash
conda activate geosaurus_dev_env
```
1.  Create a working branch for editing documentation
```git
git checkout -b new-working-branch -t upstream/master
```
> This command creates a new branch tracking the upstream repo's
  master branch.
2.  Checkout your local master branch and bring it up to date with the 
upstream repo
```git
git checkout master
```
3.  Download all the records from your upstream repo
```git 
git fetch --all
```
> This command fetches all of the changes from the upstream repository
>that have been made since the last time all records were fetched.

> This command does not merge in the changes and can be
>aborted, unlike *git pull*
4. Check the status and merge if necessary
```git
git status
```
```git
git merge upstream/master
```
5. Checkout your working branch
```git
git checkout new-working-branch
```
6. Edit the docstrings you intend to change and save them.
7. Add the changes to your branch
```git
git add paths_to_files_if_necessary
```
> Depending upon your edits, you may need to append specific paths to 
> files after the add command

> `git add .` will add all changes that occur within your current path
8. Build the documentation to inspect the changes you made:
```bash
make html
```
9. Navigate in your file browser to the `geosaurus/docs/api_ref/build/html`
directory in your repo and open the _index.html_ file with your web browser
of choice

## Tips and Suggestions

1.  Always render the local documentation before issuing a pull request
to the repo. This baseline for comparing changes to the current doc will
avoid merge conflicts.

2.  Sphinx is finicky and particular. Small changes to a table or code 
snippet could easily break the corresponding _class_ documentation, 
preventing it from rendering. To avoid hours of debugging, break your
edits into smaller modules of work (10-15 methods depending on length and 
volume of changes\. At a stopping point, save your work (add
changes to your local branch) and render local documentation to ensure 
proper rendering. If something has gone wrong, you will be working with 
a smaller amount of changes to debug.

3.  The search command on your IDE is integral to finding the right methods 
and properties in the source code to verify how and wher they render in the 
live document at `https://developers.arcgis.com/python/api-reference`.

4.  When dealing with properties, there are often two similar entries
in the source code: a _getter_ and a _setter_.
  * A getter is decorated with **@property**,  while a setter is decorated 
with **@property.setter**. However, only the docstring of the getter
will be rendered for that specific property. Any changes made to the 
**@property.setter** docstring will be disregarded in the final html output. 
However, both docstrings should be edited for consistency\!

5.  Attention to spacing is **imperative**\! Especially for _notes_, 
_warnings_, _tables_, _return_, and _code-block_ directives. (See below for 
details on these). Make sure that there is a blank space before the start and
at the end of of **every** _note_, _warning_, _table_, and _code-block_.

    ![Blank_line_illustration](./imgs/spacing_demo.png)
    
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