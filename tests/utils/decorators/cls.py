from os import environ
from parameterized import parameterized, parameterized_class

credentials_properties = ("connection_name", "portal_url", "username", "password")
standard_enterprise_credentials = (
    "standard_enterprise",
    environ.get(
        "STANDARD_ENTERPRISE_URL", "https://pythonapi.playground.esri.com/portal"
    ),
    environ.get("STANDARD_ENTERPRISE_USERNAME", "esri_requests"),
    environ.get("STANDARD_ENTERPRISE_PASSWORD", "portalaccount1"),
)
agol_api_key_credentials = (
    "agol_api_key",
    "https://www.arcgis.com",
    None,
    "AAPKddd59ccb5147417c89cc5a933c60cf51nGh5AkuWMHell2cLvgIjjRmrMRGLBqlKvpAnOPN6sHIOpc-SDkAuqTzW3vEvLkOP",
)

standard_enterprise_only = parameterized_class(
    credentials_properties,
    [
        standard_enterprise_credentials,
    ],
)

agol_api_key_only = parameterized_class(
    credentials_properties,
    [
        agol_api_key_credentials,
    ],
)
