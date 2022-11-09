"""
The ``arcgis.graph`` module contains classes and functions for working with ArcGIS Knowledge graphs. The available 
functions allow for searching and querying the graph data, and viewing the data model of the graph database. 

Knowledge graphs consist of entities and the relationships between them, each of which can contain properties which describe 
their attributes. The data model of the knowledge graph can show you which entities, relationships, and properties are in 
your database, along with other information about the graph. Performing a search or openCypher query on the graph will 
return results from the database based on the search or query terms provided.

.. note::
    For ArcGIS Enterprise 10.9.1 and 11.0, use ArcGIS API for Python version 2.0.1. For ArcGIS Enterprise at 11.1 and later, use ArcGIS API for Python version 2.1.0 or later.
"""

from arcgis.graph._service import KnowledgeGraph