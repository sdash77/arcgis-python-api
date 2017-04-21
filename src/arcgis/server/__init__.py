"""
   Entry into ArcGIS Server REST API
"""
from ._service import Service
from .managers import Server
__version__ = "1.0"
__all__ = ['Service', 'Server']

