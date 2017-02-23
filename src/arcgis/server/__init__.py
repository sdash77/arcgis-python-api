"""
   Entry into ArcGIS Server REST API
"""
from ._service import Layer
from .managers import Server
__version__ = "1.0"
__all__ = ['Layer', 'Server']

