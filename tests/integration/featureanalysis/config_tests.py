import datetime
import requests
import pandas as pd
from requests_ntlm import HttpNtlmAuth

# from requests_negotiate_sspi import HttpNegotiateAuth
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.gis import ProfileManager
from bs4 import BeautifulSoup

# scrape server page for a Kubernetes URL
def get_kube_server(site="https://rpublicservers.esri.com/AEoK1100.php", row=2):

    page = requests.get(site, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")
    links = rows[row].find_all("a")
    server_url = links[0].get("href")
    return server_url


# scrape credentials page for Kubernetes credentials
def get_kube_credentials(
    site="https://ragsreports.ags.esri.com/information/11.0_users.htm", row=16
):
    # for Windows users (make sure to uncomment import at top):
    # page = requests.get(site, auth=HttpNegotiateAuth())

    # for Mac users, use your avworld credentials below
    page = requests.get(site, auth=HttpNtlmAuth("username", "password"))

    soup = BeautifulSoup(page.content, "html.parser")
    rows = soup.find("table").find_all("tr")
    boxes = rows[row].find_all("td")
    username = boxes[0].get_text()
    password = boxes[1].get_text()
    return (username, password)


# make sure profiles are set up with proper accounts
def setup_profiles(
    online_name="online_test", ent_name="ent_test", kube_name="kube_test"
):
    # remove profiles if they already exist
    profile_list = ProfileManager().list()
    for profile in [online_name, ent_name, kube_name]:
        if profile in profile_list:
            ProfileManager().delete(profile)

    ProfileManager().create(
        online_name,
        url="https://www.arcgis.com",
        username="arcgis_python",
        password="amazing_arcgis_123",
    )

    ProfileManager().create(
        ent_name,
        url="https://gpportal.esri.com/portal/",
        username="admin",
        password="esri.agp",
    )

    ProfileManager().create(
        kube_name,
        url=get_kube_server(),
        username=get_kube_credentials()[0],
        password=get_kube_credentials()[1],
    )
