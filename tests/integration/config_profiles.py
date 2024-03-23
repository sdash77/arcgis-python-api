"""
This configuration file will check and reset all profiles for running gis module integration tests.
If the parameter "reset" for setup_profiles() set as "True", all existing profiles will be reset,
and non-existing profiles will be added.
"""
from arcgis.gis import ProfileManager

def setup_profiles(
    online_name="your_online_profile",
    online_admin_name="your_online_admin_profile",
    online_api_data_owner_name="your_online_api_data_owner_profile",
    ent_name="your_enterprise_profile",
    ent_admin_name="your_ent_admin_profile",
    kube_name="your_kubernetes_profile",
    kube_admin_name="your_kubernetes_admin_profile",
    reset=False,
):
    """create profiles"""
    all_profiles = [
        online_name,
        ent_name,
        online_admin_name,
        ent_admin_name,
        online_api_data_owner_name,
        kube_name,
        kube_admin_name,
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

    if not online_api_data_owner_name in updated_list:
        pm.create(
            online_api_data_owner_name,
            url="https://www.arcgis.com",
            username="api_data_owner",
            password="donot3xposeme",
        )
        print(f"Created profile {online_api_data_owner_name}")

    if not ent_name in updated_list:
        pm.create(
            ent_name,
            url="https://pythonapitest.dev.geocloud.com/portal/",
            username="arcgis_python",
            password="amazing_arcgis_123",
        )
        print(f"Created profile {ent_name}")

    if not ent_admin_name in updated_list:
        pm.create(
            ent_admin_name,
            url="https://pythonapitest.dev.geocloud.com/portal/",
            username="arcgispyapibot",
            password="geosaurus_automation123",
        )
        print(f"Created profile {ent_admin_name}")

    if not kube_name in updated_list:
        pm.create(
            kube_name,
            url="https://k8s.python.geocloud.com/arcgis/home",
            username="PAPIpublisher",
            password="PAPIletmein01%",
        )
        print(f"Created profile {kube_name}")
    
    if not kube_admin_name in updated_list:
        pm.create(
            kube_admin_name,
            url="https://k8s.python.geocloud.com/arcgis/home",
            username="PAPIadmin",
            password="PAPIletmein01%",
        )
        print(f"Created profile {kube_admin_name}")

    print("------------------")
    print(pm.get(online_name))
    print(pm.get(online_admin_name))
    print(pm.get(online_api_data_owner_name))
    print(pm.get(ent_name))
    print(pm.get(ent_admin_name))
    print(pm.get(kube_name))
    print(pm.get(kube_admin_name))
    print("------------------")

if __name__ == "__main__":
    setup_profiles(reset=True)
