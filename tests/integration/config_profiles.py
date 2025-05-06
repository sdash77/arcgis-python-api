"""
This configuration file will check and reset all profiles for running gis module integration tests.
If the parameter "reset" for setup_profiles() set as "True", all existing profiles will be reset,
and non-existing profiles will be added.
"""

from arcgis.gis import ProfileManager


def setup_profiles(
    online_name="your_online_profile",
    online_admin_name="your_online_admin_profile",
    online_anonymous_name="your_anonymous_online_profile",
    online_api_data_owner_name="your_online_api_data_owner_profile",
    online_admin_publication_name="your_online_admin_publication_profile",
    ent_name="your_enterprise_profile",
    ent_admin_name="your_ent_admin_profile",
    kube_name="your_kubernetes_profile",
    kube_admin_name="your_kubernetes_admin_profile",
    devext_admin_name="your_dev_online_profile",
    utility_network_name="your_utility_network_profile",
    workflow_manager_name="your_workflow_manager_profile",
    reset=False,
):
    """create profiles"""
    all_profiles = [
        online_name,
        ent_name,
        online_admin_name,
        online_anonymous_name,
        ent_admin_name,
        online_api_data_owner_name,
        online_admin_publication_name,
        kube_name,
        kube_admin_name,
        devext_admin_name,
        utility_network_name,
        workflow_manager_name,
    ]

    pm = ProfileManager()
    profile_list = pm.list()

    # remove profiles if they already exist
    if reset is True:
        for profile in all_profiles:
            if profile in profile_list:
                pm.delete(profile)
                print("Deleted " + profile)

    updated_list = pm.list()

    if not online_name in updated_list:
        pm.create(
            online_name,
            url="https://www.arcgis.com",
            username="arcgis_python",
            password="amazing_arcgis_123",
        )
        print(f"Created profile {online_name}")

    if not online_admin_name in updated_list:
        pm.create(
            online_admin_name,
            url="https://www.arcgis.com",
            username="arcgispyapibot",
            password="geosaurus_automation123",
        )
        print(f"Created profile {online_admin_name}")

    if not online_anonymous_name in updated_list:
        pm.create(
            online_anonymous_name,
            url="https://www.arcgis.com",
            username=None,
            password=None,
        )
        print(f"Created profile {online_anonymous_name}")

    if not online_api_data_owner_name in updated_list:
        pm.create(
            online_api_data_owner_name,
            url="https://www.arcgis.com",
            username="api_data_owner",
            password="donot3xposeme",
        )
        print(f"Created profile {online_api_data_owner_name}")

    if not online_admin_publication_name in updated_list:
        pm.create(
            online_admin_publication_name,
            url="https://pythonapi.maps.arcgis.com",
            username="python_api_test",
            password="esri.agp2",
        )
        print(f"Created profile {online_admin_publication_name}")

    if not ent_name in updated_list:
        pm.create(
            ent_name,
            url="https://pythonapitestnb.dev.geocloud.com/portal/",
            username="arcgis_python",
            password="amazing_arcgis_123",
        )
        print(f"Created profile {ent_name}")

    if not ent_admin_name in updated_list:
        pm.create(
            ent_admin_name,
            url="https://pythonapitestnb.dev.geocloud.com/portal/",
            username="arcgispyapibot",
            password="geosaurus_automation123",
        )
        print(f"Created profile {ent_admin_name}")

    if not kube_name in updated_list:
        pm.create(
            kube_name,
            url="https://1140pubbi-1140pubbi.apps.openshift416release.esri.com/web",
            username="PAPIpublisher",
            password="PAPIletmein01",
        )
        print(f"Created profile {kube_name}")

    if not kube_admin_name in updated_list:
        pm.create(
            kube_admin_name,
            url="https://1140pubbi-1140pubbi.apps.openshift416release.esri.com/web",
            username="PAPIadmin",
            password="PAPIletmein01",
        )
        print(f"Created profile {kube_admin_name}")

    if not devext_admin_name in updated_list:
        pm.create(
            profile=devext_admin_name,
            url="https://devgeosaurus.mapsdevext.arcgis.com",
            username="esrirequests",
            password="portalaccount1",
            key_file=None,
            cert_file=None,
            client_id=None,
        )
        print(f"Created profile {devext_admin_name}")

    if not utility_network_name in updated_list:
        pm.create(
            utility_network_name,
            url="https://utilitynetwork.esri.com/portal",
            username="python_api_team",
            password="python_api_team.109",
        )
        print(f"Created profile {utility_network_name}")

    if not workflow_manager_name in updated_list:
        pm.create(
            workflow_manager_name,
            url="https://mcstest165.esri.com/portal",
            username="admin",
            password="esri.agp",
        )
        print(f"Created profile {workflow_manager_name}")

    print("------------------")
    print(pm.get(online_name))
    print(pm.get(online_admin_name))
    print(pm.get(online_anonymous_name))
    print(pm.get(online_api_data_owner_name))
    print(pm.get(online_admin_publication_name))
    print(pm.get(ent_name))
    print(pm.get(ent_admin_name))
    print(pm.get(kube_name))
    print(pm.get(kube_admin_name))
    print(pm.get(devext_admin_name))
    print(pm.get(utility_network_name))
    print(pm.get(workflow_manager_name))
    print("------------------")


if __name__ == "__main__":
    setup_profiles(reset=True)
