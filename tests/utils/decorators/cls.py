from parameterized import parameterized, parameterized_class

credentials_properties = ("portal_name", "portal_url", "username", "password")
vanilla_enterprise_credentials = ("standard_enterprise", "https://pythonapi.playground.esri.com/portal", "esri_requests", "portalaccount1")

standard_enterprise_only = parameterized_class(
    credentials_properties,
    [
        vanilla_enterprise_credentials,
    ],
)
