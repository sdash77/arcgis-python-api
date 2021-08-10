**<span class="underline">Summary:</span>**

This document serves as a guideline and wiki for contributing to the
documentation of the ArcGIS API for Python. It includes a brief overview
of the workflow for managing through Git daily, tips and advice for
efficient work and debugging, and some common code shortcuts and syntax
for decoration.

**<span class="underline">Workflow:</span>**

Managing git can become cumbersome but starting a daily workflow to
establish consistent code practices and avoid merge conflicts when
pushing upstream.

Use the following steps to maintain an updated working branch:

1.  *git stash or git commit (if there are any uncommitted changes)*
    
      - This command is used to save uncommitted changes on your working
        branch before merging updates
    
      - **Note:** If changes are stashed, use the command *git stash
        apply* to reapply the changes

2.  *git checkout master*
    
      - This command switches from the working branch to the master
        branch

3.  *git fetch -- all*
    
      - This command fetches all of the changes to the master repository
        that have been made since the last call of this command
    
      - **Note:** This command does not merge in the changes and can be
        aborted, unlike *git pull*

4.  *git merge origin/master*
    
      - This command merges in the changes to the local master branch
        that have been downloaded from the master repository
    
      - **Note:** *git fetch – all* and this command work in combination
        to achieve the same result as *git pull*

5.  *git checkout “working-branch-name”*
    
      - This command switches back to the working branch

6.  *git merge origin/master*
    
      - This command merges the local changes into the working branch

7.  *git status*
    
      - **Note:** This command is used in order to check the status of
        your branch, see what files have been modified, and if any files
        have been added (but not committed). Use this command routinely
        to check up on your working branch.

Use the following steps to activate the geosaurus development
environment and locally render the documentation files:

8.  cd “*C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\”*
    
      - This command switches to the *envs* folder in the ArcGIS bin (if
        ArcGIS Pro is installed)

9.  *Deactivate*
    
      - This command deactivates the current environment, if one is
        activated.

10. *activate geosaurus\_dev\_env*
    
      - This command activates the *geosaurus\_dev\_env* environment,
        which has the libraries and packages installed that allow a user
        to render documentation locally from edited files on the working
        branch.

> or

11. *Deactivate*
    
      - This command deactivates the current environment, if one is
        activated.

12. *"C:\\Program
    Files\\ArcGIS\\Pro\\bin\\Python\\Scripts\\activate.bat"
    geosaurus\_dev\_env*
    
      - This command activates the *geosaurus\_dev\_env* environment,
        which has the libraries and packages installed that allow a user
        to render documentation locally from edited files on the working
        branch.
    
      - 
Use the following steps to locally render the documentation files to see
new changes made on the working branch (**This will only run if Sphinx
is installed and the geosaurus\_dev\_env environment is activated**):

13. *cd C:\\Users\\..\\..\\geosaurus\\docs\\api\_ref\\*
    
      - This command moves to the *api\_ref* folder in the geosaurus
        repository. This folder holds the restructured text (.rst) files
        that are used to render the documentation.

14. *make.bat html*
    
      - This command is used to generate html files of the
        documentation, which can be opened in a browser to view the
        changes in the documentation.

**<span class="underline">Tips/Advice:</span>**

1.  Always render the local documentation before adding any changes to
    serve as a baseline for comparing changes to the original document.

2.  Sphinx is finicky, and a small change to a table or code snippet
    could easily stop a class’s documentation from rendering. To avoid
    hours of debugging, break your work down into smaller modules of
    work (10-15 methods depending on length and amount of changes). At a
    stopping point, save your work and render local documentation to
    ensure functionality. If something has gone wrong, you will be
    working with a smaller amount of changes to debug.

3.  The location and organization of methods, and therefore their
    documentation, is not standardized across the ArcGIS API for Python
    – the search command on your IDE is integral to finding the right
    methods and properties.

4.  When dealing with properties, there are typically two property
    methods: a getter and a setter. A getter is decorated with
    *@property* while a setter is decorated with *@property.setter*.
    However, only the docstring of the getter (decorated with
    *@property*) will be rendered for that specific property. Therefore,
    any changes made to the *@property.setter* docstring will be
    disregarded by the rendering files. However, both docstrings should
    be changed to ensure accordance for the property\!

5.  Spacing is imperative, especially to notes, warnings, tables, and
    code snippets. Make sure that there is a blank space before the
    start of every note, warning, table, and code snippet as well as
    afterwards.

**<span class="underline">Syntax/Code Shortcuts:</span>**

1.  **Decorations**
    
    1.  Bold
        
        1.  \*\*Bold Text\*\* **Bold Text**
    
    2.  Italics
        
        2.  \`Italics\` *Italics*
    
    3.  Box with red lettering
        
        3.  \`\`as\_dict\`\` ![](media/image1.png)

2.  **Note creation**
    
    1.  .. note::
    
    2.  Anything indented on the lines following this decorator will be
        included in the note, until a blank line interrupts the note.
    
    3.  **Code**

*.. note::  
The \`\`append\`\` method is only available in ArcGIS Online and ArcGIS
Enterprise 10.8.1+*

4.  **Documentation Outcome**

![](media/image2.png)

3.  **Warning creation**
    
    4.  .. warning::
    
    5.  Anything indented on the lines following this decorator will be
        included in the warning, until a blank line interrupts the
        warning.
    
    6.  **Code**

*.. warning::  
Follow best security practices when sharing any HTML page that  
prompts a user for a password.*

7.  **Documentation outcome**

![](media/image3.png)

4.  **Hyperlinks**
    
    8.  To create a hyperlink, use the following format:
        
        4.  **\`**Hyperlink Text \<www.url.com\>\`\_ (**do not forget
            the underline at the end\!)**
    
    9.  **Code**

*\`Append (Feature Service/Layer)
\<https://developers.arcgis.com/rest/services-reference/append-feature-service-layer-.htm\>\`\_*

10. **Documentation Outcome**
    
    5.  ![](media/image4.png)

<!-- end list -->

5.  **Cross-reference:**
    
    11. A cross-reference is used to link to another class, method, or
        property by inserting a hyperlink-esque decoration to the text
    
    12. Class example:
        
        6.  :class:\`~arcgis.features.FeatureLayerCollection\`
            ![](media/image5.png)
    
    13. Method/Property example:
        
        7.  :attr:\`~arcgis.gis.Item.layers\`

6.  **Tables**
    
    14. Tables are quite finicky, and require care when editing. They
        require stringent spacing and line requirements.
    
    15. To create the top and bottom borders of a table, use the “=”
        symbol.
    
    16. To designate a new row of the table, use the “-“ symbol.
    
    17. To designate the start of a new column, use 5 blank spaces.
    
    18. **Code**
        
        8.  ![](media/image6.png)
    
    19. **Documentation Outcome**
        
        9.  ![](media/image7.png)
        
        10. 
7.  **Code Block**
    
    20. .. code-block:: python
    
    21. Creates a code block in the code that appears as a Python
        Snippet
    
    22. Using the \>\>\> decorator at the start of a line applies
        highlights to the line of code, such as changing the color of
        parameter names and parameter values (the snippet looks more
        like it is actual code rather than a snippet in a docstring)
    
    23. **Code**

> *.. code-block:: python  
>   
> \# Usage Example  
>   
> \>\>\> feature\_layer.append(source\_table\_name= "Building",  
> field\_Mappings=\[{"name" : "CountyID",  
> "sourceName" : "GEOID10"}\],  
> upsert = True,  
> append\_fields = \["fieldName1", "fieldName2",...., fieldname22\],  
> return\_messages = False)  
> \<True\>*

24. **Documentation Outcome**

![](media/image8.png)

8.  **Sample Method**
    
    25. **Code**

*The \`\`fromitem\`\` method creates a
:class:\`~arcgis.features.FeatureLayer\` from a
:class:\`~arcgis.gis.Item\`  
object.  
  
\===============================
====================================================================  
\*\*Argument\*\* \*\*Description\*\*  
\-------------------------------
--------------------------------------------------------------------  
item Required :class:\`~arcgis.gis.Item\` object. The type of item
should be a  
\`\`Feature Service\`\` that represents a
:class:\`~arcgis.features.FeatureLayerCollection\`  
\-------------------------------
--------------------------------------------------------------------  
layer\_id Required Integer. the id of the layer in feature layer
collection (feature service).  
The default for \`\`layer\_id\`\` is 0.  
\===============================
====================================================================  
  
.. code-block:: python  
  
\# Usage Example  
  
\>\>\> from arcgis.features import FeatureLayer  
  
\>\>\> gis = GIS("pro")  
\>\>\> buck = gis.content.search("owner:"+ gis.users.me.username)  
\>\>\> buck\_1 =buck\[1\]  
\>\>\> buck\_1.type  
'Feature Service'  
\>\>\> new\_layer= FeatureLayer.fromitem(item = buck\_1)  
\>\>\> type(new\_layer)  
\<class 'arcgis.features.layer.FeatureLayer'\>  
  
:returns:  
A :class:\`~arcgis.features.FeatureSet\` object*

26. **Documentation Code**

![](media/image9.png)
