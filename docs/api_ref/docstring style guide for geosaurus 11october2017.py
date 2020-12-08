# -*- coding: cp1252 -*-
# Purpose >> REFERENCE MODEL FOR DOCUMENTING YOUR CODE (12OCT2017)


# TOC
## 1 ## The main model
## 2 ## Standards for filling in the argument-description table
## 3 ## Standard return statements or formats
## 4 ## Table for one or two or 12 arguments
## 5 ## Table for longggg arguments
## 6 ## Maximum line length
## 7 ## Full gis.Item.create_tile_service example
## 8 ## Full gis.Item.add example, shows use of additional reference table and note
## 9 ## Full gis.ContentManager.search example, a note with a list
## 10 ## Dictionary options table for Argument item_properties, standard table
## 11 ## How to do bulleted lists
## 12 ## Code blocks for multiple
## 13 ## Format of docstrings for Python properties
## 14 ## Standard text -- data types, Esri product names, argument descriptions
## 15 ## Misc, other guidance
## very bottom ## Notes/tasks from the documentation writers on things to tackle


## 1 ## The main model
#        Honor the indentations/alignment, and the vertical and horizontal spacing!!  List
#        arguments in order.  Everything is required except the note and example code block.
#        Simply copy-n-paste the full doc string, and then edit the text to match your code.

def xyz(self, arg1, argument2=None, argument_three=None, arg4demoPruposes=None):
    """
    This is the method description, which is required.  Provide a simple and clear statement
    about what the method does/accmomplishes.  If more sentences are needed/justified,
    certainly add the info.  Try not to use the word 'Returns' here, and instead use
    Retrieves or Obtains, gets for Python properties.

    .. note::
        Optional. Any additional info that should be provided can go here. What denotes a note
        versus a method description? Hard to say, but maybe go with this guidance: if the
        information/text are suggestions or helpful things to know, put it in a note; otherwise
        it should be part of the main description of the method; or perhaps it belongs with a
        particular argument description.  URLs should go here or with the particular argument
        description.


    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    arg1                   Required string. Description text here.  See #2 below!!!!!!
    ------------------     --------------------------------------------------------------------
    argument2              Optional integer. Description text here.
    ------------------     --------------------------------------------------------------------
    argument_three         Optional string. Description text here.
    ------------------     --------------------------------------------------------------------
    arg4demoPurposes       Optional <> object. Description text here.
    ------------------     --------------------------------------------------------------------
    arg5demoPurposes       Optional <> object. Description text here. To learn more see
                           `hyperlink text <url such as : http://stackoverflow.com/>`_.
                           Note: the trailing _ is important.
    ==================     ====================================================================


    :return:
       Required. Provide a statement on the expected return from the method.  Generally, it is
       a good idea to include the data type.  For standard returns, please use a standard return
       sentence or format below (#3).


    .. code-block:: python  (optional)

       USAGE EXAMPLE: Give a description of what the example does.

       write_code_here = example for printing users in a group
       response = group.get_members()
       for user in response['users']:
            print user

    """

    

## 2 ## Standards for filling in the argument-description table

"""
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        arg1example            Required string. Generally, provide a description as a sentence,
                               although a phrase can be appropiate.
        ------------------     --------------------------------------------------------------------
        argument2              Required integer. Use sentence case for both (the optional/required
                               and data type phrase, and the description)!
        ------------------     --------------------------------------------------------------------
        argument_three         Optional string. Always provide the optional/required modifier and
                               the data type first, followed by a description of the argument. 
        ------------------     --------------------------------------------------------------------
        arg4demoPurposes       Optional integer. Always spell out the data type.  Integer not int,
                               Dictionary not dict.
        ------------------     --------------------------------------------------------------------
        fifthArgument          Optional float. This dangle past the column borders is fine, just keep the length
                               readable for developers in the code (100-ish characters).  Dangles past
                               the argument column will cause table failure.  See #5 below.
        ------------------     --------------------------------------------------------------------
        6thArgument            Optional geometry object. If there are valid values that are only 
                               allowed, provide them here with the description.
        ------------------     --------------------------------------------------------------------
        arg7Argument           Optional string. If there is a default value, provide it.  In the
                               case of booleans, be explicit about what the meaning of the default
                               value is.
        ==================     ====================================================================
"""

## 3 ## Standard return statements or formats
#        No rigidity intended here at all.  Go with what is useful for the user and jives with you.  But if 
#        it is a standard response, like a simple True or False return, please try to use the standards below.
#        In general, do not use "JSON" in return statements.
"""
For operations done to items with IDs returned or None:
   The <item ID, group ID, etc> if successfully <added, updated, deleted, etc>, None otherwise.

For simple boolean checks:
   A boolean indicating success (True) or failure (False).

For a boolean when an action is expected to be done, use:
   True if the <relationship was deleted, item was added, etc>, False if the <deletion failed, item was not successfully, etc>.

For json responses:
   A <type/item> object.


**Also on returns, do not start the return statement with 'Returns' -- that word is already there.

**And, speak to the positive/expected outcome first and with conviction...
  -not ‘the item should be updated’,
  preferred is ‘The item is updated’ 
  -or, not this 'None if the data item is not found at that path and the data item object if its found',
  but this instead 'The data item object, None if not found.' 

"""
       
## 4 ## Table for one or two or 12 arguments
"""
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        arg1                   Required string. Description text here.
        ==================     ====================================================================


        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        arg1                   Required string. Description text here.
        ------------------     --------------------------------------------------------------------
        argument2              Optional string. Description text here.
        ==================     ====================================================================


        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        arg1                   Required string. Description text here.
        ------------------     --------------------------------------------------------------------
        arg2                   Optional integer. Description text here.
        ------------------     --------------------------------------------------------------------
        arg3                   Optional string. Description text here.
        ------------------     --------------------------------------------------------------------
        arg4                   Optional integer. Description text here.
        ------------------     --------------------------------------------------------------------
        arg5                   Required string. Description text here.
        ------------------     --------------------------------------------------------------------
        arg6                   Optional integer. Description text here.
        ------------------     --------------------------------------------------------------------
        arg7                   Optional string. Description text here.
        ------------------     --------------------------------------------------------------------
        arg8                   Optional <> object. Description text here.
        ------------------     --------------------------------------------------------------------
        arg9                   Required string. Description text here.
        ------------------     --------------------------------------------------------------------
        arg10                  Optional integer. Description text here.
        ------------------     --------------------------------------------------------------------
        arg11                  Optional string. Description text here.
        ------------------     --------------------------------------------------------------------
        arg12                  Optional integer. Description text here.
        ==================     ====================================================================
"""

        
## 5 ## Table for longggg arguments
#        If the argument name goes past the argument column boundary, the table will not be produced.
#        The same does not hold true for the description column -- it is fine to flow text past this 
#        boundary, but do try to keep it reasonable if only for readability for developers in the
#        code.  See #6 below.

"""

        =======================     ====================================================================
        **Argument**                **Description**
        -----------------------     --------------------------------------------------------------------
        arg1                        Required string. Description text here.
        -----------------------     --------------------------------------------------------------------
        argument2                   Optional integer. Description text here.
        -----------------------     --------------------------------------------------------------------
        argument_three              Optional string. Description text here.
        -----------------------     --------------------------------------------------------------------
        arg4demoPurposes            Optional string. Description text here.
        =======================     ====================================================================


        ============================     ====================================================================
        **Argument**                     **Description**
        ----------------------------     --------------------------------------------------------------------
        arg1                             Required string. Description text here.
        ----------------------------     --------------------------------------------------------------------
        argument2                        Optional integer. Description text here.
        ----------------------------     --------------------------------------------------------------------
        argument_three                   Optional string. Description text here.
        ----------------------------     --------------------------------------------------------------------
        arg4demoPurposes                 Optional integer. Description text here.
        ============================     ====================================================================


        ====================================     ====================================================================
        **Argument**                             **Description**
        ------------------------------------     --------------------------------------------------------------------
        arg1                                     Required string. Description text here.
        ------------------------------------     --------------------------------------------------------------------
        argument2                                Optional integer. Description text here.
        ------------------------------------     --------------------------------------------------------------------
        argument_three                           Optional string. Description text here.
        ------------------------------------     --------------------------------------------------------------------
        arg4demoPurposes                         Optional integer. Description text here.
        ====================================     ====================================================================

"""
## 6 ## Maximum line length
#        Let's go with keeping lines at less than 100.  There was a lot of back and forth on this.  In the end,
#        it sort-of doesn't matter as shpinx inforces it's own bounds regardless of where we put line breaks.
#        PEP-8 says <80, but caveats some teams prefer 100, some on this team wanted 120 or 100.  We're going
#        with 100-ish.  Feel free to go with less, just don't exceed 100.
#        https://www.python.org/dev/peps/pep-0008/#maximum-line-length
                                                                       

## 7 ## Full gis.Item.create_tile_service example

def create_tile_service(self,
                         title,
                         min_scale,
                         max_scale,
                         cache_info=None,
                         build_cache=False):
    """
    Allows publishers and administrators to publish hosted feature
    layers and hosted feature layer views as a tile service.

    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    title             Required string. The name of the new service
                      |br|Example: "SeasideHeightsNJTiles"
    ----------------  ---------------------------------------------------------------
    min_scale         Required float. The smallest scale at which to view data.
                      Example: 577790.0
    ----------------  ---------------------------------------------------------------
    max_scale         Required float. The largest scale at which to view data.
                      Example: 80000.0
    ----------------  ---------------------------------------------------------------
    cache_info        Optional dictionary. If not none, administrator provides the
                      tile cache info for the service. The default is the ArcGIS Online scheme.
    ----------------  ---------------------------------------------------------------
    build_cache       Optional boolean. Default is False; if True, the cache will be
                      built at publishing time.  This will increase the time it takes
                      to publish the service.
    ================  ===============================================================

    :return:
       The item ID if successfully added, None if unsuccessful.

    """


## 8 ## Full gis.Item.add example, shows use of additional reference table and note
        
    def add(self, item_properties, data=None, thumbnail=None, metadata=None, owner=None, folder=None):
        """
        Adds content to the GIS by creating an item.

        .. note::
            Content can be a file (such as a service definition, shapefile,
            CSV, layer package, file geodatabase, geoprocessing package,
            map package) or it can be a URL (to an ArcGIS Server service,
            WMS service, or an application).

            If you are uploading a package or other file, provide a path or
            URL to the file in the data argument.

            From a technical perspective, none of the item_properties (see
            table below *Key:Value Dictionary Options for Argument
            item_properties*) are required.  However, it is strongly
            recommended that arguments title, type, typeKeywords, tags,
            snippet, and description be provided.


        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item_properties     Required dictionary. See table below for the keys and values.
        ---------------     --------------------------------------------------------------------
        data                Optional string. Either a path or URL to the data.
        ---------------     --------------------------------------------------------------------
        thumbnail           Optional string. Either a path or URL to a thumbnail image.
        ---------------     --------------------------------------------------------------------
        metadata            Optional string. Either a path or URL to the metadata.
        ---------------     --------------------------------------------------------------------
        owner               Optional string. Defaults to the logged in user.
        ---------------     --------------------------------------------------------------------
        folder              Optional string. Name of the folder where placing item.
        ===============     ====================================================================


        *Key:Value Dictionary Options for Argument item_properties*


        =================  =====================================================================
        **Key**            **Value**
        -----------------  ---------------------------------------------------------------------
        type               Optional string. Indicates type of item, see URL 1 below for valid values.
        -----------------  ---------------------------------------------------------------------
        typeKeywords       Optional string. Provide a lists all sub-types, see URL 1 below for valid values.
        -----------------  ---------------------------------------------------------------------
        description        Optional string. Description of the item.
        -----------------  ---------------------------------------------------------------------
        title              Optional string. Name label of the item.
        -----------------  ---------------------------------------------------------------------
        url                Optional string. URL to item that are based on URLs.
        -----------------  ---------------------------------------------------------------------
        text               Optional string. For text based items such as Feature Collections & WebMaps
        -----------------  ---------------------------------------------------------------------
        tags               Optional string. Tags listed as comma-separated values, or a list of strings.
                           Used for searches on items.
        -----------------  ---------------------------------------------------------------------
        snippet            Optional string. Provide a short summary (limit to max 250 characters) of the what the item is.
        -----------------  ---------------------------------------------------------------------
        extent             Optional string. Provide comma-separated values for min x, min y, max x, max y.
        -----------------  ---------------------------------------------------------------------
        spatialReference   Optional string. Coordinate system that the item is in.
        -----------------  ---------------------------------------------------------------------
        accessInformation  Optional string. Information on the source of the content.
        -----------------  ---------------------------------------------------------------------
        licenseInfo        Optional string.  Any license information or restrictions regarding the content.
        -----------------  ---------------------------------------------------------------------
        culture            Optional string. Locale, country and language information.
        -----------------  ---------------------------------------------------------------------
        access             Optional string. Valid values are private, shared, org, or public.
        -----------------  ---------------------------------------------------------------------
        commentsEnabled    Optional boolean. Default is true, controls whether comments are allowed (true)
                           or not allowed (false).
        =================  =====================================================================


        :return:
           The item ID if successfully added, None if unsuccessful.
        """



## 10 ## Full gis.ContentManager.search example, a note with a list
#         The line-up of numbers and paragraph lines matters.

    def search(self, query, item_type=None, sort_field='avgRating', sort_order='desc', max_items=10, outside_org=False):
        """
        Searches for portal items.

        .. note::
            A few things that will be helpful to know...

            1. The query syntax has many features that can't be adequately
               described here.  The query syntax is available in ArcGIS Help.
               A short version of that URL is http://bitly.com/1fJ8q31.

            2. Most of the time when searching for items, you'll want to
               search within your organization in ArcGIS Online
               or within your Portal.  As a convenience, the method
               automatically appends your organization id to the query by
               default.  If you want content from outside your organization
               set outside_org to True.

        ================  ==========================================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------------------------
        query             Required string. A query string.  See notes above.
        ----------------  --------------------------------------------------------------------------
        item_type         Optional string. Set type of item to search.
                          http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000ms000000
        ----------------  --------------------------------------------------------------------------
        sort_field        Optional string. Valid values can be title, uploaded, type, owner, modified,
                          avgRating, numRatings, numComments, and numViews.
        ----------------  --------------------------------------------------------------------------
        sort_order        Optional string. Valid values are asc or desc.
        ----------------  --------------------------------------------------------------------------
        max_items         Optional integer. Maximum number of items returned, default is 10.
        ----------------  --------------------------------------------------------------------------
        outside_org       Optional boolean. Controls whether to search outside your org (default is False, do not search ourside your org).
        ================  ==========================================================================

        :return:
            A list of items matching the specified query.
        """


## 10 ## Dictionary options table for Argument item_properties, standard table
#         Have seen this one used a lot and I have updated it with corrections.
"""
        *Key:Value Dictionary Options for Argument item_properties*


        =================  =====================================================================
        **Key**            **Value**
        -----------------  ---------------------------------------------------------------------
        type               Optional string. Indicates type of item, see URL 1 below for valid values.
        -----------------  ---------------------------------------------------------------------
        typeKeywords       Optional string. Provide a lists all sub-types, see URL 1 below for valid values.
        -----------------  ---------------------------------------------------------------------
        description        Optional string. Description of the item.
        -----------------  ---------------------------------------------------------------------
        title              Optional string. Name label of the item.
        -----------------  ---------------------------------------------------------------------
        url                Optional string. URL to item that are based on URLs.
        -----------------  ---------------------------------------------------------------------
      **text               Optional string. For text based items such as Feature Collections & WebMaps
        -----------------  ---------------------------------------------------------------------
        tags               Optional string. Tags listed as comma-separated values, or a list of strings.
                           Used for searches on items.
        -----------------  ---------------------------------------------------------------------
        snippet            Optional string. Provide a short summary (limit to max 250 characters) of the what the item is.
        -----------------  ---------------------------------------------------------------------
        extent             Optional string. Provide comma-separated values for min x, min y, max x, max y.
        -----------------  ---------------------------------------------------------------------
        spatialReference   Optional string. Coordinate system that the item is in.
        -----------------  ---------------------------------------------------------------------
        accessInformation  Optional string. Information on the source of the content.
        -----------------  ---------------------------------------------------------------------
        licenseInfo        Optional string.  Any license information or restrictions regarding the content.
        -----------------  ---------------------------------------------------------------------
        culture            Optional string. Locale, country and language information.
        -----------------  ---------------------------------------------------------------------
        access             Optional string. Valid values are private, shared, org, or public.
        -----------------  ---------------------------------------------------------------------
        commentsEnabled    Optional boolean. Default is true, controls whether comments are allowed (true)
                           or not allowed (false).
        =================  =====================================================================

"""

## Another way to embed table within a table
def create(self,
           name,
           url,
           events="ALL",
           number_of_failures=5,
           days_in_past=5,
           secret=None):
    """
    Creates a WebHook to monitor REST endpoints and report activities

    =================================  ===============================================================================
    **Argument**                       **Description**
    ---------------------------------  -------------------------------------------------------------------------------
    name                               Required String. The name of the webhook.
    ---------------------------------  -------------------------------------------------------------------------------
    url                                Required String. This is the URL to which the webhook will deliver payloads to.
    ---------------------------------  -------------------------------------------------------------------------------
    events                             Otional List or String.  The events accepts a list or all events can be
                                       monitored. This is done by passing "ALL" in as the events.  If a list is
                                       provided, a specific endpoint can be monitored.

                                       To create tables like below, use this web tool: http://www.tablesgenerator.com/text_tables
                                       and choose to generate in "plain english"

                                        **Item Trigger Events**

                                        +------------------------------------------------+-------------------------+
                                        | **Trigger event**                              | **URI example**         |
                                        +------------------------------------------------+-------------------------+
                                        | All trigger events for all items               | /items                  |
                                        +------------------------------------------------+-------------------------+
                                        | Add item to the portal                         | /items/add              |
                                        +------------------------------------------------+-------------------------+
                                        | All trigger events for a specific item         | /items/<itemID>         |
                                        +------------------------------------------------+-------------------------+
                                        | Delete a specific item                         | /items/<itemID>/delete  |
                                        +------------------------------------------------+-------------------------+
                                        | Update a specific item's properties            | /items/<itemID>/update  |
                                        +------------------------------------------------+-------------------------+
                                        | Move an item or changing ownership of the item | /items/<itemID>/move    |
                                        +------------------------------------------------+-------------------------+
                                        | Publish a specific item                        | /items/<itemID>/publish |
                                        +------------------------------------------------+-------------------------+
                                        | Share a specific item                          | /items/<itemID>/share   |
                                        +------------------------------------------------+-------------------------+
                                        | Unshare a specific item                        | /items/<itemID>/unshare |
                                        +------------------------------------------------+-------------------------+

                                        **Group Trigger Events**

                                        +------------------------------------------------+-------------------------------+
                                        | **Trigger event**                              | **URI example**               |
                                        +------------------------------------------------+-------------------------------+
                                        | All trigger events for all groups              | /groups                       |
                                        +------------------------------------------------+-------------------------------+
                                        | Add group                                      | /groups/add                   |
                                        +------------------------------------------------+-------------------------------+
                                        | All trigger events for a specific group        | /groups/<groupID>             |
                                        +------------------------------------------------+-------------------------------+
                                        | Update a specific group                        | /groups/<groupID>/update      |
                                        +------------------------------------------------+-------------------------------+
                                        | Delete a specific group                        | /groups/<groupID>/delete      |
                                        +------------------------------------------------+-------------------------------+
                                        | Enable Delete Protection for a specific group  | /groups/<groupID>/protect     |
                                        +------------------------------------------------+-------------------------------+
                                        | Disable Delete Protection for a specific group | /groups/<groupID>/unprotect   |
                                        +------------------------------------------------+-------------------------------+
                                        | Invite a user to a specific group              | /groups/<groupID>/invite      |
                                        +------------------------------------------------+-------------------------------+
                                        | Add a user to a specific group                 | /groups/<groupID>/addUsers    |
                                        +------------------------------------------------+-------------------------------+
                                        | Remove a user from a specific group            | /groups/<groupID>/removeUsers |
                                        +------------------------------------------------+-------------------------------+
                                        | Update a user's role in a specific group       | /groups/<groupID>/updateUsers |
                                        +------------------------------------------------+-------------------------------+


                                        **User Trigger Events**

                                        +----------------------------------------------------+---------------------------+
                                        | **Trigger event**                                  | **URI example**           |
                                        +----------------------------------------------------+---------------------------+
                                        | All trigger events for all users in the portal     | /users                    |
                                        +----------------------------------------------------+---------------------------+
                                        | All trigger events associated with a specific user | /users/<username>         |
                                        +----------------------------------------------------+---------------------------+
                                        | Delete a specific user                             | /users/<username>/delete  |
                                        +----------------------------------------------------+---------------------------+
                                        | Update a specific user's profile                   | /users/<username>/update  |
                                        +----------------------------------------------------+---------------------------+
                                        | Disable a specific user's account                  | /users/<username>/disable |
                                        +----------------------------------------------------+---------------------------+
                                        | Enable a specific user's account                   | /users/<username>/enable  |
                                        +----------------------------------------------------+---------------------------+

                                       Example Syntax: ['/users', '/groups/abcd1234....']

    ---------------------------------  -------------------------------------------------------------------------------
    number_of_failures                 Optional Integer. The number of failures to allow before the service
    ---------------------------------  -------------------------------------------------------------------------------
    days_in_past                       Option Integer. The number of days to report back on.
    ---------------------------------  -------------------------------------------------------------------------------
    secret                             Optional String. Add a Secret to your payload that can be used to authenticate
                                       the message on your receiver.
    =================================  ===============================================================================

    :returns WebHook

    """
    pass
        
## 11 ## How to do bulleted lists

#         Bulleted lists need to be in this format:
"""
- Item 1.
- Item 2.
- Item 3.


This results in "<bullet> Rest <dash> Exposes..."  :
    
- Rest -- Exposes the REST-ful API
- Soap -- Exposes the SOAP API
"""

## 12 ## How to do code blocks
#         Put these code blocks (usage examples) below the return statement.
"""
        
  Two or more example

                                                                       
  
        .. code-block:: python
        
            USAGE EXAMPLE 1: Anonymous Login to ArcGIS Online
            
            gis = GIS()

        .. code-block:: python
            
            USAGE EXAMPLE 2: Built-in Login to ArcGIS Online

            gis = GIS(username="someuser", password="secret1234")

        .. code-block:: python
            
            USAGE EXAMPLE 3: Built-in Login to ArcGIS Enterprise

            gis = GIS(url="http://pythonplayground.esri.com/portal", 
                      username="user1", password="password1")
        
"""
        


## 13 ## Format of docstrings for Python properties
#
# Always provide the doc string for both the getter and setter on the getter only.
# Format - Still TBD



## 14 ## Standard text -- data types, Esri product names, argument descriptions
##

 #
 # Data Types:
 #
"""
Always include the modifier first -- Optional or Required
Then the type followed by a period, and then followed by the argument description.

integer
string
float
boolean
dictionary
<type> object -- type being: geometry, layer, map, 
list??? string list or
?? add more
"""
 #
 # Esri product names, or related terms
 #
"""
big data, Big Data ??
Data Store, datastore, data store ??
?? add more


 #
 # Common, static arguments and their standard description
 #
culture -- Locale, country and language information.
tags -- Optional string. Tags listed as comma-separated values, or a list of strings. Used for searches on items.
access -- Optional string. Valid values are private, shared, org, or public.
?? add more
"""



## 15 ## Misc, other guidance
"""
Line character length in Python file does not matter because Sphinx dictates/overrides
any line breaks in the file.  Still Pythonic-wise, best to keep lines to ?? 75, 79, 80,
100, 120 ?? >>>> let's go with 100-ish.

Spaces between sentences should be one space (typography states this).  (Per the sentences
in this doc, it is still my habit to do two spaces, trying to break it).  Regardless, Sphinx
forces/fixes this, but let’s try to be correct in the Python file, too.

Full sentences generally.  Phrases can be called for, but generally let's be formal and adhere 
to proper grammar, punctuation, spelling, and case.

Be formal, practical and technical, but not high formal.

Spell out all words.  Use dictionary not dict, integer not int.

Known abbreviations are fine (but, don’t assume, many of our users are not developers
per se).  If using an abbreviation, capitalize all letters (URL not url) -- this applies to
descriptions, not to arguments (an argument of url stays as url).  

For Returns, don’t start with ‘Returns the list of…’, otherwise it says ‘Returns:  Returns
the list of…’.

All Notes should be between the method description and the argument-description table.

Avoid passive voice - uses more words, less logical (the object should be doing something
to the subject, not vice-versa),  less clear (with subject as start, that’s focus and clear
who is doing what).

Be succinct.  Don’t be unnecessarily wordy. Explicit, informative, but not repetitive.

Be explicit.  Cater to our users which can range from developers to GIS specialists and
system admins (all with 0-20+ years experience) who have to do these sort of things the API  
allows; and many are new to our platform. 

Generally avoid pronoun use, but when you do use these, ensure pronoun-reference agreement.

Write in the second person (you!).  Address the user specifically.

Sphinx does not like these quotes ‘on-premise GIS’ (angled, curly), must be these quotes
'on-premise GIS' (straight up-down).

For class descriptions, generally do not provide details on the methods available in the class.  
Summarize the capabilities succinctly.  Instead provide details in the method description. *1 below.

Don’t do... but... Should use quotes or bold or italics for controls,  i.e. Click the ‘Update’
link. -- future maybe?

"""



## *1
# not this >>  

def start(self):
    """
    A server machine represents a machine on which ArcGIS Server software has been installed
    and licensed. A site is made up one or more of such machines that work together to host GIS
    services and data and provide administrative capabilities for the site. Each server machine
    is capable of performing all these tasks and hence a site can be thought of as a distributed
    peer-to-peer network of such machines.

    A server machine communicates with its peers over a range of TCP and UDP ports that can be
    configured using the edit operation. For a server machine to host GIS services, it needs to
    be added to a cluster. Starting and stopping the server machine enables and disables,
    respectively, its ability to host GIS services. The administrative capabilities of the server
    machine are available through the ArcGIS Server Administrator API that can be accessed over
    HTTP(S). For a server machine to participate in a site, it must be registered with the site.
    A machine can participate in only one site at a time. To remove a machine permanently from
    the site, you can use the unregister operation.
    """
# this instead (with most of above moved to the class description) >>  
                                                                       
    def start(self):
        """
        Starts this server machine. Starting the machine enables its 
        ability to host GIS services.
        """

# Summary of above -- The two paragraphs are more suited to being in the class descriptions,
# especially since the same-ish info was repeated in several other methods.  Move those paragraphs
# to the class description, and also don't mention specific methods by name in the class description.


## *2
# help them out

# instead of:
# Can be one of SEVERE, WARNING, INFO, FINE, VERBOSE, DEBUG.  The default is WARNING.
#
# do this:
# Can be one of (in severity order): DEBUG, VERBOSE, FINE, INFO, WARNING, SEVERE. The default is WARNING.


""" Notes/tasks from the documentation writers on things to tackle

-- Provide the default list of data types... wondering about string versus string list
where appropriate... should it read 'Required string. The list of users to invite.' or
'Required string list. The users to invite as a list.' or
'Required string. The users to invite as a list.'??  #14 
-- how to do methods with no arguments, only self?  Simply no arg/desc table and go from method
description to returns statement?  or have a 'Arguments = none' statement? Former is preferred
-- should methods that are essentially the same in what is required and produced reference each
other, in particular with regards to the arg-desc table?  Ex - gis.GroupManager. create and create_from_dict ?
-- standard wording for helper classes.
-- Python properties wording.
-- Formal wording for our products... like datastore objects (datastore, or Data Store or ?) #14 
-- Add more information to items like gis.server.DataStoreManager.config, where we should provide the list
   of possible data store config properties, not just detail one of those properties; and
   gis.server.DataStoreManager.get_relational_datastore_type, provide list of possible datastore
   type IDs ??? esri.teradata, esri.sqlserver, esri.hana, any others?; gis.server.DataStoreManager.search types;
   These lists should be a static URL we can refer to for any method where these lists would apply.
-- Details on the dictionary representing the data item, per gis.server.DataStoreManager.add, example.  The 
   link is not exactly helpful.
-- Big Data vs big data vs bigdata ??  keystore #14 


"""

                               
