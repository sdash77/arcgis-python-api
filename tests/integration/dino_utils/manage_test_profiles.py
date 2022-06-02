import json
from arcgis.gis import login_profiles
import os


# Check if profile exists, else create it
def create_test_profiles(profile_json_path=None):
    if profile_json_path is None:
        profile_json_path = os.path.join("..", "..", "test_profiles.json")

    with open(profile_json_path, 'r') as file_handle:
        profile_dict = json.load(file_handle)
    print("=============TEST LOGIN PROFILE MANAGER===============")
    print(f"Profiles found in JSON: {profile_dict['profiles'].keys()}")

    profiles_on_sys = login_profiles.list()
    print(f"Following profiles were found on this computer: {profiles_on_sys} \n")

    for profile in list(profile_dict['profiles'].keys()):
        if profile not in profiles_on_sys:
            print(f"{profile} not found. Creating... ", end=" ")
            p_name = profile_dict['profiles'][profile]
            p_url = profile_dict['profiles'][profile]['url']
            p_username = profile_dict['profiles'][profile]['username']
            p_password = profile_dict['profiles'][profile]['password']

            result = login_profiles.create(profile=p_name, url=p_url, username=p_username, password=p_password)
            print(result)


if __name__ == "__main__":
    create_test_profiles()
