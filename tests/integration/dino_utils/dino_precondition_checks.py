# -------------------------------------------------------------------------------
# Name:        dino_precondition_checks.py
# Purpose:     This file checks if pre conditions are met before running the Python tests
# -------------------------------------------------------------------------------
import sys
import os
import configparser
import json


class PreconditionChecks:
    """
    Class with methods that can check if pre-conditions are met before running the tests
    """

    @staticmethod
    def get_OS():
        """
        The API works on all 3 major OS. This method is just to find the platform OS report it.
        Expand this if some components will not work on a particular OS
        :return: string representing the OS
        """
        platform = sys.platform
        return platform

    @staticmethod
    def check_API_import():
        """Check if ArcPy can be imported successfully
        Returns bool - True / False"""
        try:
            import arcgis
        except ImportError:
            print("PreConditionCheck: ArcGIS Python API cannot be imported")
            return False
        else:
            return True

    @staticmethod
    def check_ArcPy_import():
        """Check if ArcPy can be imported successfully
        Returns bool - True / False"""
        try:
            import arcpy
        except ImportError:
            return False
        else:
            return True

    @staticmethod
    def check_Pro_installed():
        """Check if ArcGISPro is installed
        Returns bool - True / False"""
        try:
            import arcpy

            installInfo = arcpy.GetInstallInfo()
            if installInfo.get("ProductName") == "ArcGISPro":
                return True
            else:
                print("Installed local GIS: " + installInfo.get("ProductName"))
                return False
        except ImportError:
            return False

    @staticmethod
    def check_Python_version():
        """Checks if Python version is 3.4 and above
        Returns bool"""
        if (sys.version_info.major >= 3) & (sys.version_info.minor >= 4):
            print("PreConditionCheck: Python version: " + sys.version)
            return True
        else:
            print("PreConditionCheck: Incompatible Python Version: " + sys.version)
            return False

    @staticmethod
    def check_Pro_is_running():
        """To expand in future. This is to find if Pro is running for cases where the API uses Pro's active portal and
        active token"""
        pass

    @staticmethod
    def can_ping_portal(url):
        """
        This is to check if portal is alive and can be reached
        :return: bool
        """
        import urllib

        try:
            resp = urllib.request.urlopen(url)
            if resp.status == 200:
                return True
            else:
                return False
        except urllib.error.URLError:
            return False


class PortalUtils:
    """
    Class to set a base state on the portal. Utilities to search, delete old outputs on portals can be found here.
    Add more utilities as need arises.
    """

    @staticmethod
    def search_portal_item(gis, item_name, item_type):
        """
        Utility to search content on portal
        :param gis: The GIS connection object to the portal
        :param item_name: Name of the item to be searched
        :param item_type: `type` property of the item to be searched
        :return: `arcgis.gis.Item` / None
        """
        try:
            search_result = gis.content.search(item_name, item_type)
            if len(search_result) > 0:
                return search_result[0]
            else:
                return None

        except Exception as search_Ex:
            print("Exception occurred : ", search_Ex.__str__())
            return None

    @staticmethod
    def report_portal_version(gis):
        """
        Utility to search content on portal
        :param gis: The GIS connection object to the portal
        :return: Version number as string
        """
        try:
            return gis.admin.properties.version

        except Exception as search_Ex:
            print(
                "Exception. You might not have admin permission to get version: ",
                search_Ex.__str__(),
            )
        return ""

    @staticmethod
    def delete_portal_item(gis, item):
        """
        Utility to delete the portal item. Validates the item is deleted by searching for it after delete.
        :param gis: `arcgis.gis.GIS` object to the portal
        :param item: `arcgis.gis.Item` object to be deleted
        :return: (bool, str) Tuple representing if delete passed or failed.
        """
        try:
            delete_result = item.delete()
            if not delete_result:
                return (False, "Delete method returned False")

            search_result = None
            try:
                search_result = gis.content.get(item.itemid)
                if search_result is not None:
                    return (False, "Deleted item can still be found on portal")
                else:
                    return (True, None)
            except RuntimeError:
                return (True, None)  # Item not found after deletion

        except Exception as delete_ex:
            print("Exception occurred : ", delete_ex.__str__())
            return (False, "Exception: " + delete_ex.__str__())

    @staticmethod
    def create_sample_users(gis):
        """
        Creates the following users in the portal
        1. arcgis_portal_api / sharing.1
        2. publisher1 / sharing.1
        3. publisher2 / sharing.1
        4. user1 / sharing.1
        5. user2 / sharing.1
        If users are already present, it skips over
        :param gis: The GIS connection object with admin privileges
        :return: True on success. False on any failure and prints error
        """
        # Create user data
        user_names = ["arcgis_python_api", "publisher1", "publisher2", "user1", "user2"]
        user_password = "sharing.1"
        last_name = "dino"
        role_list = [
            "org_admin",
            "org_publisher",
            "org_publisher",
            "org_user",
            "org_user",
        ]
        email = "amani@esri.com"

        # Check if user is present, else create
        index = 0
        return_value = True
        for user in user_names:
            try:
                print("Creating user: " + user, end=" ")
                user_obj_list = gis.users.get(user)
                if user_obj_list is None:
                    created_user = gis.users.create(
                        user,
                        user_password,
                        user,
                        last_name,
                        email,
                        role=role_list[index],
                    )
                    if created_user is not None:
                        print("Created new user: " + user)
                    else:
                        print("Error: cannot create new user: " + user)
                else:
                    print(user + " already exists in this portal")
            except Exception as ex:
                print("Error running create_sample_users: " + ex.__str__())
                return_value = False
            index += 1
        return return_value

    @staticmethod
    def create_sample_groups(gis):
        """
        Creates the following groups in the portal
        1. group1
        2. group2
        3. group3
        :param gis: The GIS connection object to the portal
        :return: True on success. False on any failure and prints error
        """
        group_names = ["group1", "group2", "group3"]
        tags = "arcgis_python_api,automation,dino_tests"
        return_value = True

        for group in group_names:
            try:
                print("Creating ", group, end=" ")
                search_result = gis.groups.search(group, max_groups=1)
                if len(search_result) > 0 and search_result[0].title == group:
                    print(" already exists..")
                    continue
                else:
                    created_group = gis.groups.create(group, tags)
                    if created_group is not None:
                        print(" succeeded")
                    else:
                        print("  error creating group")
                        return_value = False
            except Exception as group_ex:
                print(" error: " + group_ex.__str__())
                return_value = False
        return return_value

    @staticmethod
    def create_sample_groups_150(gis):
        """
        Creates the following groups in the portal
        1. group_150_1
        2. group_150_2
        3. group_150_3.. etc until 150
        :param gis: The GIS connection object to the portal
        :return: True on success. False on any failure and prints error
        """
        tags = "arcgis_python_api,dino_tests,stress_tests"
        return_value = True

        for group_index in range(1, 151):
            try:
                print("Creating ", str(group_index), end=" ")
                group_name = "group_150_" + str(group_index)
                search_result = gis.groups.search(group_name, max_groups=1)
                if len(search_result) > 0 and search_result[0].title == group_name:
                    print(" already exists..")
                    continue
                else:
                    created_group = gis.groups.create(group_name, tags)
                    if created_group is not None:
                        print(" succeeded")
                    else:
                        print("  error creating group")
                        return_value = False
            except Exception as group_ex:
                print(" error: " + group_ex.__str__())
                return_value = False
        return return_value

    @staticmethod
    def add_users_to_groups(gis):
        """
        Adds known users to known groups
        :param gis:
        :return: bool
        """
        user_names = ["arcgis_python_api", "publisher1", "publisher2", "user1", "user2"]
        group_names = ["group1", "group2", "group3"]
        return_value = True

        for group in group_names[:2]:  # only adding users to group1, group2
            group_search = gis.groups.search("title : " + group, max_groups=1)
            if group_search is not None and len(group_search) > 0:
                group_obj = group_search[0]

                for user in user_names:
                    try:
                        add_result = group_obj.add_users([user])
                        print(str(add_result))
                    except:
                        return_value = False
                        continue
        return return_value

    @staticmethod
    def add_users_to_150groups(gis):
        """
        Adds known users to known 150 groups
        :param gis:
        :return: bool
        """
        user_names = [
            "arcgis_python_api",
            "publisher1",
            "user1",
        ]
        group_index = range(1, 151)
        return_value = True

        for group in group_index:  # only adding users to group1, group2
            group_name = "group_150_" + str(group)
            group_search = gis.groups.search("title : " + group_name, max_groups=1)
            if group_search is not None and len(group_search) > 0:
                group_obj = group_search[0]

                for user in user_names:
                    try:
                        add_result = group_obj.add_users([user])
                        print(str(add_result))
                    except:
                        return_value = False
                        continue
        return return_value

    @staticmethod
    def create_sample_content_set1(gis, base_path):
        """
        Create set 1 content on portal. Use this with publisher 1 and create_sample_content_set2 for publisher2
        :param gis: GIS connection obj for publisher1
        :return: True on success. False on any failure and prints error
        """
        import pathlib
        from glob import glob1

        # function to add and publish
        def add_and_publish(
            file,
            gis,
            item_properties={},
            publish_item=False,
            folder=None,
            publish_parameters={},
        ):
            # check if such an item exists
            file_name = ""
            if file is None:
                # happens for text based items
                file_name = item_properties["title"]
                file_name_wextn = file_name
            else:
                file_name = pathlib.Path(file).stem  # gives file name without extension
                file_name_wextn = pathlib.Path(file).name

            print("Adding " + file_name_wextn, end=" ")
            sr = gis.content.search("title:" + file_name, max_items=1)
            if sr is not None and len(sr) > 0:
                print(" already exists")
                return True

            sr2 = gis.content.search("title:" + file_name_wextn, max_items=1)
            if sr2 is not None and len(sr2) > 0:
                print(" already exists")
                return True

            sr3 = gis.content.search("name:" + file_name_wextn, max_items=1)
            if sr3 is not None and len(sr3) > 0:
                print(" already exists")
                return True

            sr4 = gis.content.search(file_name_wextn, max_items=1)
            if sr4 is not None and len(sr4) > 0:
                print(" already exists")
                return True
            else:
                # Add item
                try:
                    added_item = gis.content.add(item_properties, file, folder=folder)
                except Exception as addEx:
                    print("Item add exception: " + addEx.__str__())
                    return False
                if added_item is not None:
                    if publish_item:
                        try:
                            published_item = added_item.publish()
                        except Exception as pubEx:
                            print("Publish Exception: " + pubEx.__str__())
                            return False

                        if published_item is not None:
                            print(" published")
                            return True
                        else:
                            print(" added but cannot be published")
                            return False
                    else:
                        print(" added successfully")
                        return True
                else:
                    print(" error adding as item")
                    return False

        # add and publish csv files
        print("Adding CSV files")
        file_path = os.path.join(base_path, "csv")
        file_list = glob1(file_path, "set1*.csv")
        for file in file_list:
            add_and_publish(os.path.join(file_path, file), gis, publish_item=True)
        print("-----------------------------------------------------------")

        # add and publish fgdb
        print("Adding fgdb")
        file_path = os.path.join(base_path, "fgdb")
        file_list = glob1(file_path, "set1*.zip")
        for file in file_list:
            add_and_publish(os.path.join(file_path, file), gis, publish_item=True)
        print("-----------------------------------------------------------")

        # add and publish geojson
        print("Adding geojson files")
        file_path = os.path.join(base_path, "geojson")
        file_list = glob1(file_path, "set1*.json")
        item_properties = {"type": "GeoJson"}
        for file in file_list:
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
            )
        print("-----------------------------------------------------------")

        # Add some image files (jpeg, png etc)
        print(
            "Adding image files - illustrating how a user would have project files in a folder"
        )
        file_path = os.path.join(base_path, "images")
        file_list = glob1(file_path, "set1*.png")
        item_properties = {"type": "Image"}
        for file in file_list:
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
                folder="f1_english",
            )
        print("-----------------------------------------------------------")

        # Add some KML
        print("Adding KML files")
        file_path = os.path.join(base_path, "kml")
        file_list = glob1(file_path, "set1*.kml")
        item_properties = {"type": "KML"}
        for file in file_list:
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
                folder="f1_english",
            )
        print("-----------------------------------------------------------")

        # Add some Locators
        print("Adding Locator files")
        file_path = os.path.join(base_path, "Locators")
        file_list = glob1(file_path, "set1*.zip")
        item_properties = {"type": "Locator Package"}
        for file in file_list:
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
                folder="f1_english",
            )
        print("-----------------------------------------------------------")

        # Add some layer files
        print("Adding layer files")
        file_path = os.path.join(base_path, "lyr")
        file_list = glob1(file_path, "set1*")
        item_properties = {"type": "KML"}
        for file in file_list:
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
                folder="f1_english",
            )
        print("-----------------------------------------------------------")

        # Add some map documents
        print("Adding map doc files")
        file_path = os.path.join(base_path, "mxd")
        file_list = glob1(file_path, "set1*.mxd")
        item_properties = {"type": "Map Document"}
        for file in file_list:
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
            )
        print("-----------------------------------------------------------")

        # Add some office files
        print("Adding office files")
        file_path = os.path.join(base_path, "office")
        file_list = glob1(file_path, "set1*")

        for file in file_list:
            extn = os.path.splitext(file)[1]
            if extn == ".docx":
                item_properties = {"type": "Microsoft Word"}
            elif extn == ".pptx":
                item_properties = {"type": "Microsoft Powerpoint"}
            elif extn == ".pdf":
                item_properties = {"type": "PDF"}
            elif extn == ".xlsx":
                item_properties = {"type": "Microsoft Excel"}
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
            )
        print("-----------------------------------------------------------")

        # Add some packages
        print("Adding arcgis packages")
        file_path = os.path.join(base_path, "packages")
        file_list = glob1(file_path, "set1*")

        for file in file_list:
            extn = os.path.splitext(file)[1]
            if extn == ".lpk":
                item_properties = {"type": "Layer Package"}
            elif extn == ".mmpk":
                item_properties = {"type": "Mobile Map Package"}
            elif extn == ".gpk":
                item_properties = {"type": "Geoprocessing Package"}
            elif extn == ".spk" or extn == ".slpk":
                item_properties = {"type": "Scene Package"}
            elif extn == ".spk" or extn == ".tpk":
                item_properties = {"type": "Tile Package"}
            elif extn == ".spk" or extn == ".vtpk":
                item_properties = {"type": "Vector Tile Package"}
            add_and_publish(
                os.path.join(file_path, file),
                gis,
                item_properties=item_properties,
                publish_item=False,
            )
        print("-----------------------------------------------------------")

        # Add some hosted SD files
        print("Adding SD files")
        temp_path = os.path.join(base_path, "SDs")
        file_path = os.path.join(temp_path, "set1")
        file_list = glob1(file_path, "W*.sd")
        for file in file_list:
            add_and_publish(os.path.join(file_path, file), gis, publish_item=True)
        print("-----------------------------------------------------------")

        # Add some hosted shape files
        print("Adding shape files")
        file_path = os.path.join(base_path, "shp")
        file_list = glob1(file_path, "set1*.zip")
        for file in file_list:
            item_properties = {"type": "Shapefile", "name": file}
            add_and_publish(
                os.path.join(file_path, file), gis, item_properties, publish_item=True
            )
        print("-----------------------------------------------------------")

        # Add some web maps
        print("Adding WebMaps")
        file_path = os.path.join(base_path, "webmap")
        file_list = glob1(file_path, "set1*.JSON")
        for file in file_list:
            with open(os.path.join(file_path, file)) as file_handle:
                webmap_def = json.load(file_handle)
                item_properties = {
                    "title": "set1_" + file.split(".")[0],
                    "type": "Web Map",
                    "text": json.dumps(webmap_def),
                }
                add_and_publish(
                    None, gis, item_properties=item_properties, publish_item=False
                )
        print("-----------------------------------------------------------")

        # Add unstyled layer items
        print("Adding unstyled layer items")
        item_properties = {
            "title": "set1_unstyled_layer1",
            "type": "Map Service",
            "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
        }
        add_and_publish(None, gis, item_properties=item_properties, publish_item=False)
        print("-----------------------------------------------------------")

        # Add empty items
        print("Adding emtpy web apps")
        item_properties = {
            "title": "set1_empty_webapp",
            "type": "Web Mapping Application",
            "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
        }
        add_and_publish(None, gis, item_properties=item_properties, publish_item=False)
        print("-----------------------------------------------------------")

    @staticmethod
    def create_sample_content_set2(gis):
        """
        Create set 2 content on portal.
        :param gis: GIS connection obj for publisher2
        :return: True on success. False on any failure and prints error
        """
        pass

    @staticmethod
    def create_sample_folders_set1(gis):
        """
        Creates the following folders:
        1. f1_english
        2. f2_敏感性增加
        3. f3_Kompatibilität
        :param gis: The GIS connection object for which these folders need to be created
        :return: True on success. False on any failure and prints error
        """
        # Search if folder already exists
        new_folder_list = ["f1_english", "f2_敏感性增加", "f3_Kompatibilität"]

        return_value = True
        for folder in new_folder_list:
            print("Creating : " + folder, end=" ")
            try:
                create_result = gis.content.folders.create(folder)
                if create_result is not None:
                    print("created")
                else:
                    print(" error")
                    return_value = False
            except Exception as folder_ex:
                print("error: " + folder_ex.__str__())
                return_value = False
                continue
        return return_value

    @staticmethod
    def create_sample_folders_set2(gis):
        """
        Creates the following folders:
        1. f1_english
        2. f2_كامتالتصويلح
        3. f3_совместимость
        :param gis:The GIS connection object for which these folders need to be created
        :return: True on success. False on any failure and prints error
        """
        new_folder_list = ["f1_english", "f2_كامتالتصويلح", "f3_совместимость"]

        return_value = True
        for folder in new_folder_list:
            print("Creating : " + folder, end=" ")
            try:
                create_result = gis.content.folders.create(folder)
                if create_result is not None:
                    print("created")
                else:
                    print(" error")
                    return_value = False
            except Exception as folder_ex:
                print("error: " + folder_ex.__str__())
                return_value = False
                continue
        return return_value
