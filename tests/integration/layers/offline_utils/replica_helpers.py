from arcgis.features.layer import FeatureLayerCollection


def get_replicas(flc: FeatureLayerCollection):
    replicas = []
    for replica in flc.replicas.get_list():
        rep = flc.replicas.get(replica["replicaID"])
        replicas.append(rep)
    return replicas


def unregister_replica(
    flc: FeatureLayerCollection, replica_id: str
):
    try:
        flc.replicas.unregister(replica_id)
        print("Unregistered replica ID: ", replica_id)
    except Exception as ex:
        print(f"Unregister {replica_id} failed:", str(ex))


def remove_orphaned_versions(flc: FeatureLayerCollection, version_str: str):
    for v in flc.versions.all:
        version_name = v.properties.versionName
        if version_str in version_name:
            flc.versions.purge(v.properties.versionName)
            v.delete()
            print("Deleted:", version_name)


def cleanup_replica_items(feature_layer_collection: FeatureLayerCollection):
    replica_versions = get_replicas(feature_layer_collection)

    print(f"Unregistering {len(replica_versions)} replicas")
    for replica in replica_versions:
        replica_id = replica["replicaID"]
        unregister_replica(feature_layer_collection, replica_id)

    print("Deleting all orphaned replica versions...")
    for v in feature_layer_collection.versions.all:
        if "admin_OfflineUse" in v.properties.versionName:
            try:
                v.delete()
                print("Deleted", v.properties.versionName)
            except Exception:
                pass
