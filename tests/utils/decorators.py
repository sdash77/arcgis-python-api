from os import environ
from parameterized import parameterized, parameterized_class
from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy

PROXIES = detect_proxy(True)  # Handles Fiddler when True

# region credential property definitions
_credentials_properties = ("connection_name", "portal_url", "username", "password")
_profiles_properties = ("profile_description", "profile")
# endregion
# region credential parameters
_enterprise_credential_parameters = (
    "enterprise",
    environ.get(
        "STANDARD_ENTERPRISE_URL", "https://pythonapi.playground.esri.com/portal"
    ),
    environ.get("STANDARD_ENTERPRISE_USERNAME", "esri_requests"),
    environ.get("STANDARD_ENTERPRISE_PASSWORD", "portalaccount1"),
)
_agol_credential_parameters = (
    "agol",
    environ.get("STANDARD_AGOL_URL", "https://www.arcgis.com"),
    environ.get("STANDARD_AGOL_USERNAME", "esri_requests"),
    environ.get("STANDARD_AGOL_PASSWORD", "portalaccount1"),
)
_agol_api_key_credential_parameters = (
    "agol_api_key",
    environ.get("AGOL_API_KEY_URL", "https://www.arcgis.com"),
    None,
    environ.get(
        "AGOL_API_KEY",
        "AAPKddd59ccb5147417c89cc5a933c60cf51nGh5AkuWMHell2cLvgIjjRmrMRGLBqlKvpAnOPN6sHIOpc-SDkAuqTzW3vEvLkOP",
    ),
)
# endregion


# region parameterized_class constructors
def _get_profile_parameterized_class(*args):
    """Returns a parameterized class for the profile parameters from provided args"""
    __profiles_properties = _profiles_properties
    _profiles_values = []
    # attempt to set gis property constructed from profile
    # in each profile configuration
    gis_set = False
    for profile_config in [*args]:
        try:
            profile_config += (
                GIS(profile=profile_config[1], verify_cert=False, proxy=PROXIES),
                PROXIES,
            )
            gis_set = True
        except Exception as e:
            pass
        _profiles_values += [profile_config]
    if gis_set:
        # at least one profile has a gis property
        # add the properties
        __profiles_properties += ("gis", "proxies")
    return parameterized_class(
        __profiles_properties,
        _profiles_values,
    )


def _get_credentials_parameterized_class(*args):
    """Returns a parameterized class for the credentials parameters from provided args"""
    return parameterized_class(
        _credentials_properties,
        [*args],
    )


# endregion

# region credential decorators
enterprise_and_agol_credentials = _get_credentials_parameterized_class(
    _enterprise_credential_parameters,
    _agol_credential_parameters,
)
enterprise_credentials = _get_credentials_parameterized_class(
    _enterprise_credential_parameters,
)

agol_api_key_credentials = _get_credentials_parameterized_class(
    _agol_api_key_credential_parameters,
)
# endregion

# region profile parameters
_agol_profile_parameters = ("agol", "your_online_profile")
_agol_admin_profile_parameters = ("agol_admin", "your_online_admin_profile")
_enterprise_profile_parameters = ("enterprise", "your_enterprise_profile")
_enterprise_admin_profile_parameters = ("enterprise_admin", "your_ent_admin_profile")


# endregion


admin_agol_profile = _get_profile_parameterized_class(_agol_admin_profile_parameters)
agol_profile = _get_profile_parameterized_class(_agol_profile_parameters)
admin_enterprise_profile = _get_profile_parameterized_class(
    _enterprise_admin_profile_parameters
)
enterprise_profile = _get_profile_parameterized_class(_enterprise_profile_parameters)
enterprise_and_agol_profiles = _get_profile_parameterized_class(
    _agol_profile_parameters, _enterprise_profile_parameters
)
admin_enterprise_and_agol_profiles = _get_profile_parameterized_class(
    _agol_admin_profile_parameters, _enterprise_admin_profile_parameters
)
