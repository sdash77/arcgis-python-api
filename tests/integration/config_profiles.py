"""
This configuration file will check and reset all profiles for running gis module integration tests.
If the parameter "reset" for setup_profiles() set as "True", all existing profiles will be reset,
and non-existing profiles will be added.
Reference: https://github.com/ArcGIS/geosaurus/pull/8683
"""
import requests
import platform
import lxml
import os
from arcgis.gis import GIS
from arcgis.gis import ProfileManager


def get_kube_server(site="https://rpublicservers.esri.com/AEoK1110.php", row=3):

    # Important note: code is based off of current rpublicservers page. If
    # page format or data gets changed, row parameter may have to be altered.
    # currently set up to find 1110publdapwa server.

    page = requests.get(site, verify=False)
    html = lxml.html.fromstring(page.content)
    table = html.xpath("//table")[0]
    links = list(table[row].iterlinks())
    server_url = links[0][2]
    return server_url


# scrape credentials page for Kubernetes credentials
def get_kube_credentials(
    site="https://ragsreports.ags.esri.com/information/11.1_users.htm", row=5
):

    # for non-Windows users, you will either have to set environment
    # variables for your AVWORLD username & password, or enter them
    # in via the command line every time you run the methods

    if platform.system() == "Windows" and os.environ.get("userdomain") == "AVWORLD":
        from requests_negotiate_sspi import HttpNegotiateAuth
        page = requests.get(site, auth=HttpNegotiateAuth())
    else:
        from requests_ntlm2 import HttpNtlmAuth

        env_dict = os.environ

        # check if env variables exist, if not set them
        # note: this does not set them permanently
        if not "AVWORLD_USERNAME" in env_dict:
            inp = input("Please enter your AVWORLD username: ")
            os.environ["AVWORLD_USERNAME"] = inp

        if not "AVWORLD_PASSWORD" in env_dict:
            inp = input("Please enter your AVWORLD password: ")
            os.environ["AVWORLD_PASSWORD"] = inp

        av_username = env_dict.get("AVWORLD_USERNAME")
        av_password = env_dict.get("AVWORLD_PASSWORD")
        page = requests.get(site, auth=HttpNtlmAuth(av_username, av_password))

    # Important note: code is based off of current ragsreports page. If page
    # format or data gets changed, row parameter may have to be altered.
    # Currently set up to get apps0001 credentials.

    html = lxml.html.fromstring(page.content)
    table = html.xpath("//table")[0]
    row_list = table.xpath("//tr")[row]
    text_list = str(row_list.text_content()).split()
    username = text_list[0]
    password = text_list[1]
    return (username, password)


def setup_profiles(
    online_name="your_online_profile",
    online_admin_name="your_online_admin_profile",
    online_api_data_owner_name="your_online_api_data_owner_profile",
    ent_name="your_enterprise_profile",
    ent_admin_name="your_ent_admin_profile",
    kube_name="your_kubernetes_profile",
    reset=False,
):
    """create profiles"""

    pm = ProfileManager()
    profile_list = pm.list()

    # remove profiles if they already exist
    if reset is True:
        for profile in [
            online_name,
            ent_name,
            online_admin_name,
            ent_admin_name,
            online_api_data_owner_name,
            kube_name,
        ]:
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
            url="https://pythonapi.playground.esri.com/portal/",
            username="arcgis_python",
            password="amazing_arcgis_123",
        )
        print(f"Created profile {ent_name}")

    if not ent_admin_name in updated_list:
        pm.create(
            ent_admin_name,
            url="https://pythonapi.playground.esri.com/portal/",
            username="arcgispyapibot",
            password="geosaurus_automation123",
        )
        print(f"Created profile {ent_admin_name}")

    if not kube_name in updated_list:
        kube_credentials = get_kube_credentials()
        pm.create(
            kube_name,
            url=get_kube_server(),
            username=kube_credentials[0],
            password=kube_credentials[1],
        )
        print(f"Created profile {kube_name}")

    print(pm.get(online_name))
    print(pm.get(online_admin_name))
    print(pm.get(online_api_data_owner_name))
    print(pm.get(ent_name))
    print(pm.get(ent_admin_name))
    print(pm.get(kube_name))


if __name__ == "__main__":
    setup_profiles(reset=True)
