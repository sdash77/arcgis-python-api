import requests
import platform
import lxml
from arcgis.gis import GIS
from arcgis.gis import ProfileManager

# add config path for featureanalysis tests
import os
import sys
fa_path = os.getcwd()
if fa_path not in sys.path:
    sys.path.insert(0, fa_path)


test_items = [
    "1ac6896bcafc4dccb29c70f45c442b00",  # Polygon Zips
    "435fcf6cff1f4f34989e151c1f25d64a",  # Esri Offices
    "c7665d3c8e6f48a79f07b79677996bed",  # Esri HQ
    "d3cb37b9636d47888268ca086810bd9b",  # Cougar Habitat
    "5183636f099c48789628226e5730fb13",  # Traffic Collisions
    "a6cb2a0688d841fd803cd82b4d8282b4",  # Boundary Polygon
    "3793ab5f2baa47919bd4212b3d0f08e2",  # LA Route Geodatabase
    "00fbc412f68645958520d946806f90c0",  # Tennessee Town
    "4147267f9bcc46e79825950d800c1e6a",  # Comparison US Towns
    "5fdb2869753140c8836353097b207591",  # US Hospitals
    "2150d4ebe2124f4c821f43de49a6c679",  # US Airports
]

# scrape server page for a Kubernetes URL
def get_kube_server(site="https://rpublicservers.esri.com/AEoK1120.php", row=1):

    # Important note: code is based off of current rpublicservers page. If
    # page format or data gets changed, row parameter may have to be altered.
    # currently set up to find 1100publdapwa server.

    page = requests.get(site, verify=False)
    html = lxml.html.fromstring(page.content)
    table = html.xpath("//table")[0]
    links = list(table[row].iterlinks())
    server_url = links[0][2]
    return server_url


# scrape credentials page for Kubernetes credentials
def get_kube_credentials(
    site='https://ragsreports.ags.esri.com/information/11.2_Users_files/sheet001.htm', username_row=8, password_row=9
):

    # for non-Windows users, you will either have to set environment
    # variables for your AVWORLD username & password, or enter them
    # in via the command line every time you run the methods

    if platform.system() is "Windows":
        from requests_negotiate_sspi import HttpNegotiateAuth

        page = requests.get(site, auth=HttpNegotiateAuth())
    else:
        from requests_ntlm2 import HttpNtlmAuth
        import os

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
    # Currently set up to get creator2 credentials.

    html = lxml.html.fromstring(page.content)
    table = html.xpath("//table")[0]
    username_row_element = table.xpath("//tr")[username_row]
    username = username_row_element.getchildren()[3].text_content()
    password_row_element = table.xpath("//tr")[password_row]
    password_string = password_row_element.getchildren()[1].text_content()
    password = password_string.split(" ")[-1]
    return (username, password)


# make sure profiles are set up with proper accounts
def setup_profiles(
    online_name="online_test",
    ent_name="ent_test",
    kube_name="kube_test",
    reset=False,
):
    # remove profiles if they already exist
    pm = ProfileManager()
    profile_list = pm.list()
    if reset is True:
        for profile in [online_name, ent_name, kube_name]:
            if profile in profile_list:
                pm.delete(profile)
                print("Deleted " + profile)

    updated_list = pm.list()

    if not online_name in updated_list:
        print("Creating online profile")
        pm.create(
            online_name,
            url="https://www.arcgis.com",
            username="arcgis_python",
            password="amazing_arcgis_123",
        )
        print(pm.get(online_name))

    if not ent_name in updated_list:
        print("Creating ent profile")
        pm.create(
            ent_name,
            url="https://pythonapitest.dev.geocloud.com/portal/",
            username="arcgis_python",
            password="amazing_arcgis_123",
        )
        print(pm.get(ent_name))

    if not kube_name in updated_list:
        print("Creating kube profile")
        pm.create(
            kube_name,
            url="https://11-1-k8s.python.geocloud.com/arcgis/home",
            username="geosaurusaccnt",
            password="geosaurus_automation123",
        )
        print(pm.get(kube_name))


# stage data from list of AGOL items into ent & kube
def stage_data(
    data_list,
    online_prof="online_test",
    ent_prof="ent_test",
    kube_prof="kube_test",
):
    # extract necessarity items from AGOL
    gis_agol = GIS(profile=online_prof, verify_cert=False)
    items = []
    for item_id in data_list:
        item = gis_agol.content.get(item_id)
        items.append(item)

    # check if they exist, if not add into ent & kube
    for prof in [ent_prof, kube_prof]:
        gis = GIS(profile=prof, verify_cert=False)
        for item in items:
            if not gis.content.get(item.id):
                if item.type == ("File Geodatabase" or "CSV"):
                    temp_path = item.get_data()
                    gis.content.add(
                        item_properties=item, data=temp_path, item_id=item.id
                    )
                else:
                    gis.content.add(item, item_id=item.id)


if __name__ == "__main__":
    setup_profiles(reset=True)
    stage_data(test_items)
