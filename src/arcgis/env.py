"""
The **env** module provides a shared environment used by the different modules.
It stores globals such as the currently active GIS, the default geocoder and so on.

active_gis
==========

.. py:data:: active_gis
The currently active GIS, that is used for analysis functions unless explicitly specified
when calling the functions.
Creating a new GIS object makes it active unless set_active=False is passed in the GIS constructor.


active_geocoder
===============

.. py:data:: active_geocoder
The currently active geocoder in the GIS, that is used for geocoding unless explicitly specified
when calling the functions.
Creating a new GIS object makes it's first available geocoder as the active geocoder
unless set_active=False is passed in the GIS constructor.
"""

#: The currently active GIS, that is used for analysis functions unless explicitly specified.
#: Creating a new GIS object makes it active by default unless set_active=False is passed in the GIS constructor.
active_gis = None

#: The currently active geocoder, that is used for geocoding unless explicitly specified.
#: Creating a new GIS object makes it's first available geocoder as the active geocoder
#: unless set_active=False is passed in the GIS constructor.
active_geocoder = None