# -------------------------------------------------------------------------------
# Name:        _prepare_portal.py
# Purpose:     This script is to be used when a mew test portal or org is created.
#               It calls the utilities in PortalUtils class to create users,
#               groups and content
#-------------------------------------------------------------------------------
import os
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
from arcgis.gis import GIS

def populate_portal_users_groups(gis):
    print("Creating Groups")
    create_groups_result = PortalUtils.create_sample_groups(gis)
    print("create groups result: " + str(create_groups_result))
    print("=============================================================")

    create_150groups_result = PortalUtils.create_sample_groups_150(gis)
    print("create 150 groups result: " + str(create_150groups_result))
    print("=============================================================")

    print("Creating users")
    create_users_result = PortalUtils.create_sample_users(gis)
    print("create users result: " + str(create_users_result))
    print("=============================================================")

    print("adding users to groups")
    add_result = PortalUtils.add_users_to_groups(gis)
    print("add users to groups result: " + str(add_result))
    print("=============================================================")

    print("adding users to 150 groups")
    add_result_150 = PortalUtils.add_users_to_150groups(gis)
    print("add users to 150 groups result: " + str(add_result_150))
    print("=============================================================")

def populate_portal_content_1(gis, data_path):
    print("Creating folders")
    PortalUtils.create_sample_folders_set1(gis)
    print("=============================================================")

    print("Creating content")
    PortalUtils.create_sample_content_set1(gis, os.path.join(data_path, "data_prep"))

def populate_portal_content_2(gis, data_path):
    print("Creating folders")
    PortalUtils.create_sample_folders_set2(gis)
    print("=============================================================")

# guard from import
if __name__ == "__main__":
    # region Read config data
    _conf_reader = ConfigParser()
    _conf_reader2 = ConfigParser()
    _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')
    _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

    portal_url = _conf_reader['teamportal']['url']
    portal_username = _conf_reader['teamportal']['admin_user']
    portal_password = _conf_reader['teamportal']['admin_password']

    my_gis = GIS(portal_url, portal_username, portal_password)
    # populate_portal_users_groups(my_gis)

    # Create content for publisher1
    portal_url = _conf_reader['arcgiscom']['url']
    pub1_username = _conf_reader['arcgiscom']['admin_user']
    pub1_password = _conf_reader['arcgiscom']['admin_password']
    data_path = _conf_reader2['test_data']['qalab_base_path']

    pub1_gis = GIS(portal_url, pub1_username, pub1_password)
    populate_portal_content_1(pub1_gis, data_path)

    # Create content for publisher2
    # portal_url = _conf_reader['teamportal']['url']
    # pub2_username = _conf_reader['teamportal']['publisher2']
    # pub2_password = _conf_reader['teamportal']['publisher2_password']
    #
    # pub2_gis = GIS(portal_url, pub2_username, pub2_password)
    # populate_portal_content_2(pub2_gis)