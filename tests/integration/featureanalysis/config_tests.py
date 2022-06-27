import datetime
import requests
import pandas as pd
import platform
import lxml
from arcgis.gis import GIS, Item
from arcgis.gis import ProfileManager

test_items = [
    "1ac6896bcafc4dccb29c70f45c442b00",  # Polygon Zips
    "b96b5740372b4b838d621716264bb21d",  # Esri Offices
    "c7665d3c8e6f48a79f07b79677996bed",  # Esri HQ
    "747b24cdf0ef49acab79feb3dfcd4546",  # Cougar Habitat
]

# scrape server page for a Kubernetes URL
def get_kube_server(site="https://rpublicservers.esri.com/AEoK1100.php", row=2):

    page = requests.get(site, verify=False)
    html = lxml.html.fromstring(page.content)
    table = html.xpath("//table")[0]
    links = list(table[row].iterlinks())
    server_url = links[0][2]
    return server_url


# scrape credentials page for Kubernetes credentials
def get_kube_credentials(
    site="https://ragsreports.ags.esri.com/information/11.0_users.htm", row=16
):

    # for non-Windows users, use your avworld credentials below

    if platform.system() is "Windows":
        from requests_negotiate_sspi import HttpNegotiateAuth

        page = requests.get(site, auth=HttpNegotiateAuth())
    else:
        from requests_ntlm import HttpNtlmAuth

        page = requests.get(site, auth=HttpNtlmAuth("USERNAME", "PASSWORD"))

    html = lxml.html.fromstring(page.content)
    table = html.xpath("//table")[0]
    row_list = table.xpath("//tr")[row]
    text_list = str(row_list.text_content()).split()
    username = text_list[0]
    password = text_list[1]
    return (username, password)


# make sure profiles are set up with proper accounts
def setup_profiles(
    online_name="online_test", ent_name="ent_test", kube_name="kube_test"
):
    # remove profiles if they already exist
    pm = ProfileManager()
    profile_list = pm.list()
    for profile in [online_name, ent_name, kube_name]:
        if profile in profile_list:
            pm.delete(profile)

    pm.create(
        online_name,
        url="https://www.arcgis.com",
        username="arcgis_python",
        password="amazing_arcgis_123",
    )

    pm.create(
        ent_name,
        url="https://gpportal.esri.com/portal/",
        username="admin",
        password="esri.agp",
    )

    pm.create(
        kube_name,
        url=get_kube_server(),
        username=get_kube_credentials()[0],
        password=get_kube_credentials()[1],
    )


# stage data from list of AGOL items into ent & kube
def stage_data(
    data_list, online_prof="online_test", ent_prof="ent_test", kube_prof="kube_test"
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
                gis.content.add(item, item_id=item.id)
