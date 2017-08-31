"""
Server Package Root

Provides access to the Catalog, Service, and Manager classes for ArcGIS
Server

"""
from .catalog import Catalog
from ._service import Service
from .sm import ServerManager
from .admin import Server
