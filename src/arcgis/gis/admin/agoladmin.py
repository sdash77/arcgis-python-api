"""
Entry point to working with local enterprise GIS functions
"""
from ..._impl.connection import _ArcGISConnection
from ...gis import GIS
from ._base import BasePortalAdmin
########################################################################
class AGOLAdminManager(object):
    """
    This is the root resource for administering your online GIS. Starting from
    this root, all of the GIS's environment is organized into a
    hierarchy of resources and operations.

    Parameter:
    :param gis: GIS object containing Administrative credentials
    :param ux: the UX object (optional)
    :param metadata: the metadata manager object (optional)
    :param collaborations: the CollaborationManager object (optional)
    """
    _gis = None
    _ux = None
    _metadata = None
    _collaborations = None
    #----------------------------------------------------------------------
    def __init__(self,
                 gis,
                 ux=None,
                 metadata=None,
                 collaborations=None):
        """initializer"""
        self._gis = gis
        self._ux = ux
        self._collaborations = collaborations
        self._metadata = metadata
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._gis._portal.resturl)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._gis._portal.resturl)
    #----------------------------------------------------------------------
    @property
    def ux(self):
        """returns a UX/UI manager"""
        if self._ux is None:
            from .. import UX
            self._ux = UX(gis=self._gis)
        return self._ux
    #----------------------------------------------------------------------
    @property
    def collaborations(self):
        """
        The collaborations resource lists all collaborations in which a
        portal participates
        """
        if self._collaborations is None:
            from .. import CollaborationManager
            self._collaborations = CollaborationManager(gis=self._gis)
        return self._collaborations
    #----------------------------------------------------------------------
    @property
    def metadata(self):
        """
        resources to work with metadata on GIS
        """
        if self._metadata is None:
            from .. import MetadataManager
            self._metadata = MetadataManager(gis=self._gis)
        return self._metadata
