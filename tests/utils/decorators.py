from os import environ, name as os_name
from parameterized import parameterized, parameterized_class
from unittest import SkipTest
from .timeout_decorator import timeout as _timeout, timeout_class as _timeout_class
from .classproperty import classproperty
from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy
from integration.config import get_resource_path

PROXIES = detect_proxy(True)  # Handles Fiddler when True

DEFAULT_TIMEOUT_SECONDS = 60
EXTENDED_TIMEOUT_SECONDS = 300
MAXIMUM_TIMEOUT_SECONDS = 600


def timeout(seconds):
    """Decorator that will timeout a test after a specified number of seconds"""
    return _timeout(
        seconds=seconds,
        timeout_exception=SkipTest,
        exception_message=f"Aborting test, timed out at {seconds} seconds",
    )


default_timeout = timeout(DEFAULT_TIMEOUT_SECONDS)
extended_timeout = timeout(EXTENDED_TIMEOUT_SECONDS)
maximum_timeout = timeout(MAXIMUM_TIMEOUT_SECONDS)


def timeout_class(seconds):
    """Decorator that will timeout all tests in a class after a specified number of seconds"""
    return _timeout_class(
        seconds=seconds,
        timeout_exception=SkipTest,
        exception_message=f"Aborting test, timed out at {seconds} seconds",
    )


default_timeout_class = timeout_class(DEFAULT_TIMEOUT_SECONDS)
extended_timeout_class = timeout_class(EXTENDED_TIMEOUT_SECONDS)
maximum_timeout_class = timeout_class(MAXIMUM_TIMEOUT_SECONDS)

def integration_test(cls):
    """Mark a test case class as an integration test and apply default configuration"""
    if os_name == "posix":
        # apply default timeout on supported platforms
        cls = default_timeout_class(cls)
    # TODO find a way to apply default timeout on Windows
    return cls

_gis_by_profile = {}


def _get_gis(profile):
    """Returns a gis for a profile"""
    if profile not in _gis_by_profile:
        _gis_by_profile[profile] = GIS(
            profile=profile, verify_cert=False, proxy=PROXIES
        )
    return _gis_by_profile[profile]


class credentials:
    """
    A set of decorators that inject credentials into tests.

    Sets the following properties on the test class:
    self.connection_name: the unique connection name, appended to the test name (e.g. agol, enterprise)
    self.portal_url: the portal url
    self.username: the username
    self.password: the password
    self.cert: the cert file path, if any

    If multiple credentials are injected, the test will be run once for each credential.
    """

    _enterprise_credential_parameters = (
        "enterprise",
        environ.get(
            "STANDARD_ENTERPRISE_URL", "https://pythonapi.playground.esri.com/portal"
        ),
        environ.get("STANDARD_ENTERPRISE_USERNAME", "esri_requests"),
        environ.get("STANDARD_ENTERPRISE_PASSWORD", "portalaccount1"),
    )
    _enterprise_pki_credential_parameters = (
        "enterprise_pki",
        environ.get(
            "ENTERPRISE_PKI_URL", "https://rqawinpki03pt.ags.esri.com/gis"
        ),
        None,
        environ.get("ENTERPRISE_PKI_PASSWORD", "portalaccount1"),
        environ.get("ENTERPRISE_PKI_CERT", get_resource_path("esri_requests/certs/creator2.pfx")),
    )
    _enterprise_java_pki_credential_parameters = (
        "enterprise_java_pki",
        environ.get(
            "ENTERPRISE_JAVA_PKI_URL", "https://rqawinjpki06pt.ags.esri.com/gis"
        ),
        None,
        environ.get("ENTERPRISE_JAVA_PKI_PASSWORD", "portalaccount1"),
        environ.get("ENTERPRISE_JAVA_PKI_CERT", get_resource_path("esri_requests/certs/creator2.pfx")),
    )
    _enterprise_linux_pki_credential_parameters = (
        "enterprise_linux_pki",
        environ.get(
            "ENTERPRISE_LINUX_PKI_URL", "https://rqalnxpki03pt.esri.com/gis"
        ),
        None,
        environ.get("ENTERPRISE_LINUX_PKI_PASSWORD", "portalaccount1"),
        environ.get("ENTERPRISE_LINUX_PKI_CERT", get_resource_path("esri_requests/certs/creator2.pfx")),
    )
    _enterprise_iwa_credential_parameters = (
        "enterprise_iwa",
        environ.get("ENTERPRISE_IWA_URL", "https://rqawiniwa02pt.ags.esri.com/gis"),
        environ.get("ENTERPRISE_IWA_USERNAME", r"avworld\creator2"),
        environ.get("ENTERPRISE_IWA_PASSWORD", "portalaccount1"),
    )
    _enterprise_multi_iwa_credential_parameters = (
        "enterprise_multi_iwa",
        environ.get("ENTERPRISE_MULTI_IWA_URL", "https://rqawinmiwa05pt.ags.esri.com/gis"),
        environ.get("ENTERPRISE_MULTI_IWA_USERNAME", r"avworld\creator2"),
        environ.get("ENTERPRISE_MULTI_IWA_PASSWORD", "portalaccount1"),
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

    def _get_credentials_parameterized_class(*args):
        """Returns a parameterized class for the credentials parameters from provided args"""
        _credentials_properties = (
            "connection_name",
            "portal_url",
            "username",
            "password",
            "cert",
        )
        """Returns a parameterized class for the credentials parameters from provided args"""
        return parameterized_class(
            _credentials_properties,
            [*args],
            # default test name is {class_name}_{index}_{connection_name}; override to remove index:
            class_name_func=lambda cls, _, param: f"{cls.__name__}_{parameterized.to_safe_name(param['connection_name'])}",
        )

    # region decorators
    @classproperty
    def enterprise(cls):
        """Run tests for enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_credential_parameters
        )
    
    @classproperty
    def enterprise_all_iwa(cls):
        """Run tests for iwa and multi-iwa enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_iwa_credential_parameters, cls._enterprise_multi_iwa_credential_parameters
        )
    
    @classproperty
    def enterprise_all_pki(cls):
        """Run tests for pki enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_pki_credential_parameters, 
            cls._enterprise_java_pki_credential_parameters, 
            cls._enterprise_linux_pki_credential_parameters
        )

    @classproperty
    def agol(cls):
        """Run tests for agol credentials"""
        return cls._get_credentials_parameterized_class(cls._agol_credential_parameters)

    @classproperty
    def enterprise_and_agol(cls):
        """Run tests for enterprise and agol credentials"""
        return cls._get_credentials_parameterized_class(
            cls._agol_credential_parameters, cls._enterprise_credential_parameters
        )

    @classproperty
    def agol_api_key(cls):
        """
        Run tests for agol api key credential

        Note: self.password represents the api key; no username is required
        """
        return cls._get_credentials_parameterized_class(
            cls._agol_api_key_credential_parameters
        )
    
    @classproperty
    def enterprise_pki(cls):
        """Run tests for enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_pki_credential_parameters
        )

    # endregion


class profiles:
    """
    A set of decorators that inject profiles into tests.

    Sets the following properties on the test class:
    self.profile_description: the unique profile description, appended to the test name (e.g. agol, agol_admin, enterprise)
    self.profile: the profile name
    self.gis: the GIS for the profile, if connection is successful
    self.proxies: the detected proxies, if any

    If multiple profiles are injected, the test will be run once for each profile.
    """

    _agol_profile_parameters = ("agol", "your_online_profile")
    _agol_admin_profile_parameters = ("agol_admin", "your_online_admin_profile")
    _enterprise_profile_parameters = ("enterprise", "your_enterprise_profile")
    _enterprise_admin_profile_parameters = (
        "enterprise_admin",
        "your_ent_admin_profile",
    )
    _k8s_profile_parameters = ("k8s", "your_kubernetes_profile")

    def _get_profile_parameterized_class(*args):
        """Returns a parameterized class for the profile parameters from provided args"""
        _profiles_properties = ("profile_description", "profile")
        __profiles_properties = _profiles_properties
        _profiles_values = []
        # attempt to set gis property constructed from profile
        # in each profile configuration
        gis_set = False
        for profile_config in [*args]:
            try:
                profile_config += (
                    _get_gis(profile_config[1]),
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
            # default test name is {class_name}_{index}_{profile_description}; override to remove index:
            class_name_func=lambda cls, _, param: f"{cls.__name__}_{parameterized.to_safe_name(param['profile_description'])}",
        )

    # region decorators
    @classproperty
    def admin_agol(cls):
        """Run tests for agol admin profile"""
        return cls._get_profile_parameterized_class(cls._agol_admin_profile_parameters)

    @classproperty
    def agol(cls):
        """Run tests for agol profile"""
        return cls._get_profile_parameterized_class(cls._agol_profile_parameters)

    @classproperty
    def admin_enterprise(cls):
        """Run tests for enterprise admin profile"""
        return cls._get_profile_parameterized_class(
            cls._enterprise_admin_profile_parameters
        )

    @classproperty
    def enterprise(cls):
        """Run tests for enterprise profile"""
        return cls._get_profile_parameterized_class(cls._enterprise_profile_parameters)

    @classproperty
    def enterprise_and_agol(cls):
        """Run tests for enterprise and agol profiles"""
        return cls._get_profile_parameterized_class(
            cls._agol_profile_parameters, cls._enterprise_profile_parameters
        )

    @classproperty
    def admin_enterprise_and_agol(cls):
        """Run tests for enterprise and agol admin profiles"""
        return cls._get_profile_parameterized_class(
            cls._agol_admin_profile_parameters, cls._enterprise_admin_profile_parameters
        )

    @classproperty
    def k8s(cls):
        """Run tests for kubernetes profile"""
        return cls._get_profile_parameterized_class(cls._k8s_profile_parameters)

    # endregion
