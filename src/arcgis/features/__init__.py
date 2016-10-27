"""
Module for working with features and feature layers in the GIS.

In the GIS, entities located in space with a set of properties can be represented as features.  Features are stored as
feature classes, which represent a set of features located using a single spatial type (point, line, polygon) and a
common set of properties.  This is the geographic extension of the classic tabular or relational representation for
entities - a set of entities is modelled as rows in a table.  Tables represent entity classes with uniform
properties.  In addition to working with “entities with location” as features, the system can also work with
non-spatial entities as rows in tables.  The system can also model relationships between entities using properties
which act as primary and foreign keys.  A collection of feature classes and tables, with the associated
relationships among the entities, is a feature layer collection. FeatureLayerCollections are one of the dataset types
contained in a Datastore.  Finally, features are not simply entities in a dataset.  Features have a visual
representation and user experience - on a map, in a 3D scene, as entities with a property sheet or popups.
"""

from .feature import Feature, FeatureSet, FeatureCollection
from .layer import FeatureLayer, Table, FeatureLayerCollection
from .managers import AttachmentManager, ReplicaManager, FeatureLayerCollectionManager, FeatureLayerManager

__all__ = ['Feature', 'FeatureSet', 'FeatureCollection', 'FeatureLayer', 'Table', 'FeatureLayerCollection']
