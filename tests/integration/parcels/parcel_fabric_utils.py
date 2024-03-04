import time
from collections import namedtuple
from typing import List
import arcgis.features
from arcgis.features import FeatureLayer, FeatureLayerCollection


def clean_up_versions(vms):
    """Delete all versions that match a search criteria.

    Args:
      vms (arcgis.features._version.VersionManager): VersionManager object

    Returns:
      void
    """
    try:
        for version in vms.all:
            if version.properties.versionName.lower().startswith("admin.api-"):
                # Purge any locks on these test versions
                vms.purge(version.properties.versionName)
                version.delete()
                print(f"deleted version: {version.properties.versionName}")
    except Exception as ex:
        print("Error deleting version(s):", str(ex))


def get_version(vms, owner_name, version_name):
    """Get an existing branch version by name

    Args:
      vms (arcgis.features._version.VersionManager): VersionManager object
      owner_name (str): The owner of the branch version to search for
      version_name (str): The name of the branch version to search for
    Returns:
      The fully qualified version name (`owner.version_name`) string
    """

    _version = [
        x
        for x in vms.all
        if x.properties.versionName.lower() == f"{owner_name}.{version_name}".lower()
    ]
    fq_version_name = _version[0].properties.versionName
    return fq_version_name


def create_version(vms, version_name=None):
    """Create a new branch version

    Args:
      vms (arcgis.features._version.VersionManager): VersionManager object
      version_name (str): (Optional) name of the version to be created
    Returns:
      The fully qualified version name (`owner.version_name`) string
    """
    try:
        timestamp = int(time.time())
        if not version_name:
            # VersionManagementServer - Create a new version
            version_name = "api-{}".format(timestamp)
        else:
            version_name = f"{version_name}_{timestamp}"
        vms.create(version_name)

        # get the fully qualified version name string as 'owner.versionName'
        _version = [
            x
            for x in vms.all
            if x.properties.versionName.lower() == "admin." + version_name
        ]
        fq_version_name = _version[0].properties.versionName
        return fq_version_name
    except Exception as ex:
        print(ex)
        return None


def _generate_where_in_clause(field_name, feature_list):
    """

    Args:
      field_name (str): Name of column to query
      feature_list (list): List of values to generate IN clause

    Returns:
        string e.g. `WHERE name IN ('a' ,'b', 'c')`
    """
    # Build up 'IN' clause for searching
    where_str = f"{field_name} in ("
    for p in feature_list:
        if not isinstance(p, str):
            where_str += f"{str(p)},"
        else:
            where_str += f"'{str(p)}',"
    where_str = f"{where_str[:-1]})"
    return where_str


def get_feature_layer(flc, lyr_name):
    """Get a FeatureLayer out of a FeatureLayerCollection by its name property

    Args:
      flc (arcgis.features.FeatureLayerCollection): The FeatureLayerCollection
      containing the desired FeatureLayer

      lyr_name (str): The name

    Returns:
      arcgis.features.FeatureLayer
    """
    fl_url = [n for n in flc.layers if n.properties.name.lower() == lyr_name.lower()]
    fl = FeatureLayer(fl_url[0].url)
    return fl


def query_service(
    url, gis, out_fields, version_name, fl_id=None, where="1=1", return_geom=False
):
    """Returns a FeatureSet containing the features matching the query

    Args:
      url (str): URL of FeatureServer service to query
      gis (GIS): GIS of feature service
      out_fields (list): list of fields t return
      version_name (str): branch version
      fl_id (int): (optional) LayerId of service
      where (str): (optional) WHERE clause to filter query

    Returns:
        arcgis.features.FeatureSet of features matching the query
    """
    if not fl_id:
        fl = arcgis.features.FeatureLayer(f"{url}", gis)
    else:
        fl = arcgis.features.FeatureLayer(f"{url}/{fl_id}", gis)
    return fl.query(
        where=where,
        out_fields=out_fields,
        return_geometry=return_geom,
        gdb_version=version_name,
    )


def create_parcel_record(flc, version_name, record_name="NewRecord001"):
    """Create a parcel record in the Records feature layer

    Args:
      flc (arcgis.Features.FeatureLayerCollection): FLC of the parcel fabric
      version_name: branch version
      record_name:  Name of the new record
                        (Default value = "NewRecord001")

    Returns:
      Dict of edited features
    """
    # Record information with empty geometry.  The geometry is created during Build
    record_dict = {"attributes": {"name": record_name}, "geometry": None}
    records_fl = get_feature_layer(flc, "records")

    # Call edit_features method on the feature_layer object
    new_record = records_fl.edit_features(adds=[record_dict], gdb_version=version_name)
    return new_record


def get_record_by_guid(gis, records_url, guid, gdb_version):
    """Query the records feature class to get back some specic attributes.

    Args:
      gis (arcgis.GIS): GIS of the service
      records_url: URL of records feature layer
      guid: GlobalID value of desired record
      gdb_version: branch version

    Returns:
      str (GUID)
    """
    where = "GLOBALID = '{}'".format(guid)
    records_fl = FeatureLayer(records_url, gis)
    record_attributes = records_fl.query(
        where=where,
        gdb_version=gdb_version,
        out_fields=["NAME", "GLOBALID"],
    ).to_dict()
    return record_attributes["features"]


def get_record_guid_by_name(gis, records_url, record_name, gdb_version):
    """Query the records feature class to get back some specic attributes.

    Args:
      gis (arcgis.GIS): GIS of the service
      records_url: URL of records feature layer
      guid: GlobalID value of desired record
      gdb_version: branch version

    Returns:
      str (GUID)
    """
    where = "NAME = '{}'".format(record_name)
    records_fl = FeatureLayer(records_url, gis)
    record_attributes = records_fl.query(
        where=where,
        gdb_version=gdb_version,
        out_fields=["NAME", "GLOBALID"],
    ).to_dict()
    return record_attributes["features"]
  
def basic_lyr_info(feature_layer_collection: FeatureLayerCollection, layer_name: str = None) -> List[namedtuple]:
  """Get a list of namedtuples containing
      - layer name
      - layer collection order number as they appear in the collection
      - the layer's layer ID
      - the url to the feature layer

      Or:
      A single named tuple described above for a specific layer

      Args:
        feature_layer_collection (arcgis.features.FeatureLayerCollection): The FeatureLayerCollection
        containing the desired FeatureLayer

        layer_name (str): (optional) The name of a layer in the collection

      Returns:
        List[namedtuple]
  """
  layers = feature_layer_collection.layers
  LayerProps = namedtuple("LayerProp", ["lyr_name", "lyr_list_order", "lyr_id", "lyr_url"])
  layer_props = []
  for i, lyr in enumerate(layers):
      lp = LayerProps(lyr.properties.name, i, lyr.properties.id, lyr.url)
      layer_props.append(lp)

  if layer_name:
      return [lyr for lyr in layer_props if lyr.lyr_name == layer_name]
  return layer_props
