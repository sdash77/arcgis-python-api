from __future__ import annotations
from typing import Any, Optional, Union
from arcgis import env
from arcgis._impl.common._mixins import PropertyMap

########################################################################
class NetworkDiagramManager(object):
    """
    The Network Diagram service resource represents a network diagram 
    service published with ArcGIS Server. The resource provides information 
    about the service itself (name, type, default diagram template) and 
    exposes various functions to access published network diagrams, create 
    new network diagrams and store them, edit and maintain network diagrams, and so on.

    The Network Diagram service supports some operations which allow 
    retrieving network diagrams, getting the characteristics of 
    the diagrams you want (diagram info, consistency state), creating new network 
    diagrams and deleting network diagrams.

    .. note::
        The active portal account must be licensed with the ArcGIS Utility Network
        user type extension or the ArcGIS Trace Network user type extension to
        use the utility network and network diagram services.

    =====================   ===========================================
    **Inputs**              **Description**
    ---------------------   -------------------------------------------
    url                     Required String. The web endpoint to the utility service.
    ---------------------   -------------------------------------------
    version                 Required Version. The `Version` class where the branch version will take place.
    ---------------------   -------------------------------------------
    gis                     Optional GIS. The `GIS` connection object.
    =====================   ===========================================


    """

    _con = None
    _gis = None
    _url = None
    _version = None
    _property = None
    _version_guid = None
    _version_name = None
    # ----------------------------------------------------------------------
    def __init__(self, url, version, gis=None):
        """Constructor"""
        if gis is None:
            gis = env.active_gis
        self._gis = gis
        self._con = gis._portal.con
        self._url = url
        self._version = version
        self._version_guid = version._guid
        self._version_name = version.properties.versionName

    # ----------------------------------------------------------------------
    def _init(self):
        """initializer"""
        try:
            res = self._con.get(self._url, {"f": "json"})
            self._property = PropertyMap(res)
        except Exception as e:
            self._property = PropertyMap({})

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """returns the properties for the service"""
        if self._property is None:
            self._init()
        return self._property
    # ----------------------------------------------------------------------
    def find_diagram_names(self, moment, extent, where, features, exclude_system_diagrams):
        """
        The findDiagramNames operation is performed on a Network Diagram Service resource. 
        The result of this operation is an array of strings, each one corresponding to 
        a network diagram's name.

        This operation is used to retrieve the set of diagrams that cover 
        a given extent, verify a particular WHERE clause, or contain specific 
        utility network features or diagram features.
        
        ==============================      =====================================================
        **Arguments**                       **Description**
        ------------------------------      -----------------------------------------------------
        moment                              Optional Integer.
        ------------------------------      -----------------------------------------------------
        extent
        ------------------------------      -----------------------------------------------------
        where
        ------------------------------      -----------------------------------------------------
        features
        ------------------------------      -----------------------------------------------------
        exclude_system_diagrams
        ==============================      =====================================================
        """
    # ----------------------------------------------------------------------
    def create_diagram_from_features(self):
        """
        
        """