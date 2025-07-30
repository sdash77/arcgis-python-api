from os import environ, name as os_name
from parameterized import parameterized, parameterized_class
from unittest import SkipTest
from .timeout_decorator import (
    timeout as _timeout,
    timeout_class as _timeout_class,
)
from .classproperty import classproperty
from ._common import environ_key_to_bool
from arcgis.gis import GIS, ProfileManager
from arcgis.auth.tools._util import detect_proxy
from integration.config import get_resource_path
from threading import TIMEOUT_MAX

profile_manager = ProfileManager()
configured_profiles = {
    profile: profile_manager._retrieve_dict(profile)
    for profile in profile_manager.list()
}

STANDARD_ENTERPRISE_PROFILE = "your_enterprise_profile"
STANDARD_ENTERPRISE_PROFILE_CONFIG = configured_profiles.get(
    STANDARD_ENTERPRISE_PROFILE, {}
)
STANDARD_ENTERPRISE_URL = environ.get(
    "STANDARD_ENTERPRISE_URL",
    STANDARD_ENTERPRISE_PROFILE_CONFIG.get("url")
    or "https://pythonapitestnb.dev.geocloud.com/portal",
)
STANDARD_ENTERPRISE_USERNAME = environ.get(
    "STANDARD_ENTERPRISE_USERNAME",
    STANDARD_ENTERPRISE_PROFILE_CONFIG.get("username") or "arcgis_python",
)
STANDARD_ENTERPRISE_PASSWORD = environ.get(
    "STANDARD_ENTERPRISE_PASSWORD",
    STANDARD_ENTERPRISE_PROFILE_CONFIG.get("password") or "amazing_arcgis_123",
)

PROXIES = detect_proxy(True)  # Handles Fiddler when True

NO_TIMEOUT = environ_key_to_bool("ARCGIS_TEST_NO_TIMEOUT")

DEFAULT_TIMEOUT_SECONDS = 60 if not NO_TIMEOUT else TIMEOUT_MAX
EXTENDED_TIMEOUT_SECONDS = 300 if not NO_TIMEOUT else TIMEOUT_MAX
MAXIMUM_TIMEOUT_SECONDS = 600 if not NO_TIMEOUT else TIMEOUT_MAX


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
    if profile not in configured_profiles:
        print(
            f"Profile '{profile}' not configured in arcgis.gis.ProfileManager, run `config_profiles.py`!"
        )
        return None
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

    _avworld_username = "creator2"
    _avworld_username_with_domain = rf"avworld\{_avworld_username}"
    _avworld_password = "portalaccount1"

    _enterprise_credential_parameters = (
        "enterprise",
        STANDARD_ENTERPRISE_URL,
        STANDARD_ENTERPRISE_USERNAME,
        STANDARD_ENTERPRISE_PASSWORD,
    )
    _enterprise_pki_credential_parameters = (
        "enterprise_pki",
        environ.get("ENTERPRISE_PKI_URL", "https://rqawinpki03pt.ags.esri.com/gis"),
        None,
        environ.get("ENTERPRISE_PKI_PASSWORD", "portalaccount1"),
        environ.get(
            "ENTERPRISE_PKI_CERT",
            get_resource_path("esri_requests/certs/creator2.pfx"),
        ),
    )
    _enterprise_java_pki_credential_parameters = (
        "enterprise_java_pki",
        environ.get(
            "ENTERPRISE_JAVA_PKI_URL",
            "https://rqawinjpki06pt.ags.esri.com/gis",
        ),
        None,
        environ.get("ENTERPRISE_JAVA_PKI_PASSWORD", "portalaccount1"),
        environ.get(
            "ENTERPRISE_JAVA_PKI_CERT",
            get_resource_path("esri_requests/certs/creator2.pfx"),
        ),
    )
    _enterprise_linux_pki_credential_parameters = (
        "enterprise_linux_pki",
        environ.get("ENTERPRISE_LINUX_PKI_URL", "https://rqalnxpki03pt.esri.com/gis"),
        None,
        environ.get("ENTERPRISE_LINUX_PKI_PASSWORD", "portalaccount1"),
        environ.get(
            "ENTERPRISE_LINUX_PKI_CERT",
            get_resource_path("esri_requests/certs/creator2.pfx"),
        ),
    )
    _enterprise_iwa_credential_parameters = (
        "enterprise_iwa",
        environ.get("ENTERPRISE_IWA_URL", "https://rqawiniwa02pt.ags.esri.com/gis"),
        environ.get("ENTERPRISE_IWA_USERNAME", _avworld_username_with_domain),
        environ.get("ENTERPRISE_IWA_PASSWORD", _avworld_password),
    )
    _enterprise_multi_iwa_credential_parameters = (
        "enterprise_multi_iwa",
        environ.get(
            "ENTERPRISE_MULTI_IWA_URL",
            "https://rqawinmiwa05pt.ags.esri.com/gis",
        ),
        environ.get("ENTERPRISE_MULTI_IWA_USERNAME", _avworld_username_with_domain),
        environ.get("ENTERPRISE_MULTI_IWA_PASSWORD", _avworld_password),
    )
    _enterprise_kerberos_credential_parameters = (
        "enterprise_kerberos",
        environ.get("ENTERPRISE_KERBEROS_URL", "https://rqawinkb08pt.ags.esri.com/gis"),
        environ.get("ENTERPRISE_KERBEROS_USERNAME", _avworld_username_with_domain),
        environ.get("ENTERPRISE_KERBEROS_PASSWORD", _avworld_password),
    )
    _enterprise_ldap_credential_parameters = (
        "enterprise_ldap",
        environ.get("ENTERPRISE_LDAP_URL", "https://rqalnxldap02pt.esri.com/gis"),
        environ.get("ENTERPRISE_LDAP_USERNAME", _avworld_username),
        environ.get("ENTERPRISE_LDAP_PASSWORD", _avworld_password),
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
            "AAPKed706a70151045f3a51b1917d84757610pwOA7fIeA6M3kLOR0_kBLPRMfwnympI0ql7knab8d6sTEJyRRKAzQBGqgP6XSDj",
        ),
    )
    _agol_oauth_credential_parameters = (
        "agol_oauth",
        environ.get("STANDARD_AGOL_URL", "https://www.arcgis.com"),
        environ.get("STANDARD_AGOL_USERNAME", "esri_requests"),
        environ.get("STANDARD_AGOL_PASSWORD", "portalaccount1"),
        None,
        environ.get("AGOL_OAUTH_CLIENT_ID", "FONLvbtoFNAFZBTm"),
        environ.get("AGOL_OAUTH_CLIENT_SECRET", "26bcc585a3b44862980abe390e85b06a"),
    )
    _enterprise_oauth_credential_parameters = (
        "enterprise_oauth",
        STANDARD_ENTERPRISE_URL,
        STANDARD_ENTERPRISE_USERNAME,
        STANDARD_ENTERPRISE_PASSWORD,
        None,
        environ.get("ENTERPRISE_OAUTH_CLIENT_ID", "8L1tmD9aVTGeUKH0"),
        environ.get(
            "ENTERPRISE_OAUTH_CLIENT_SECRET", "d916012205374179abefba3636993c18"
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
            "client_id",
            "client_secret",
        )
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
            cls._enterprise_iwa_credential_parameters,
            cls._enterprise_multi_iwa_credential_parameters,
        )

    @classproperty
    def enterprise_iwa(cls):
        """Run tests for iwa and multi-iwa enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_iwa_credential_parameters,
        )

    @classproperty
    def enterprise_kerberos(cls):
        """Run tests for kerberos enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_kerberos_credential_parameters
        )

    @classproperty
    def enterprise_ldap(cls):
        """Run tests for ldap enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_ldap_credential_parameters
        )

    @classproperty
    def enterprise_all_pki(cls):
        """Run tests for pki enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_pki_credential_parameters,
            cls._enterprise_java_pki_credential_parameters,
            cls._enterprise_linux_pki_credential_parameters,
        )

    @classproperty
    def agol(cls):
        """Run tests for agol credentials"""
        return cls._get_credentials_parameterized_class(cls._agol_credential_parameters)

    @classproperty
    def devext(cls):
        """Run tests for agol profile"""
        return cls._get_profile_parameterized_class(cls._agol_devext_profile_parameters)

    @classproperty
    def enterprise_and_agol(cls):
        """Run tests for enterprise and agol credentials"""
        return cls._get_credentials_parameterized_class(
            cls._agol_credential_parameters,
            cls._enterprise_credential_parameters,
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
    def enterprise_oauth(cls):
        """Run tests for enterprise oauth credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_oauth_credential_parameters
        )

    @classproperty
    def agol_oauth(cls):
        """Run tests for agol oauth credentials"""
        return cls._get_credentials_parameterized_class(
            cls._agol_oauth_credential_parameters
        )

    @classproperty
    def all_oauth(cls):
        """Run tests for all oauth credentials"""
        return cls._get_credentials_parameterized_class(
            cls._agol_oauth_credential_parameters,
            cls._enterprise_oauth_credential_parameters,
        )

    @classproperty
    def enterprise_pki(cls):
        """Run tests for enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_pki_credential_parameters
        )

    # endregion


class server_credentials:
    """
    A set of decorators that inject server credentials into tests.

    Sets the following properties on the test class:
    self.connection_name: the unique connection name, appended to the test name (e.g. agol, enterprise)
    self.url: the server url root (e.g. https://arcgis.enterprise.com/server) | Note: does not include `/rest` or `/rest/services`
    self.portal_url: the portal url, if the server is federated or ArcGIS Online
    self.username: the username
    self.password: the password
    """

    _enterprise_standalone_credential_parameters = (
        "standalone_enterprise",
        environ.get(
            "ENTERPRISE_STANDALONE_SERVER_URL", "https://dev0016118.esri.com/server"
        ),
        None,
        environ.get("ENTERPRISE_STANDALONE_SERVER_USERNAME", "siteadmin"),
        environ.get("ENTERPRISE_STANDALONE_SERVER_PASSWORD", "IL0veGI$"),
    )

    # region decorators
    @classproperty
    def standalone_enterprise(cls):
        """Run tests for standalone server enterprise credentials"""
        return cls._get_credentials_parameterized_class(
            cls._enterprise_standalone_credential_parameters
        )

    # endregion

    def _get_credentials_parameterized_class(*args):
        """Returns a parameterized class for the credentials parameters from provided args"""
        _credentials_properties = (
            "connection_name",
            "url",
            "portal_url",
            "username",
            "password",
        )
        return parameterized_class(
            _credentials_properties,
            [*args],
            # default test name is {class_name}_{index}_{connection_name}; override to remove index:
            class_name_func=lambda cls, _, param: f"{cls.__name__}_{parameterized.to_safe_name(param['connection_name'])}",
        )


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

    _agol_anonymous_profile_parameters = (
        "agol_anonymous",
        "your_anonymous_online_profile",
    )
    _agol_profile_parameters = ("agol", "your_online_profile")
    _agol_devext_profile_parameters = ("devext", "your_dev_online_profile")
    _agol_admin_profile_parameters = (
        "agol_admin",
        "your_online_admin_profile",
    )
    _enterprise_profile_parameters = (
        "enterprise",
        STANDARD_ENTERPRISE_PROFILE,
    )
    _enterprise_admin_profile_parameters = (
        "enterprise_admin",
        "your_ent_admin_profile",
    )
    _enterprise_devent_admin_profile_parameters = (
        "devent_admin",
        "your_dev_ent_admin_profile",
    )
    _k8s_profile_parameters = ("k8s", "your_kubernetes_profile")
    _k8s_admin_profile_parameters = (
        "k8s_admin",
        "your_kubernetes_admin_profile",
    )
    _utility_network_profile_parameters = (
        "utility_network",
        "your_utility_network_profile",
    )
    _workflow_manager_profile_parameters = (
        "workflow_manager",
        "your_workflow_manager_profile",
    )
    _parcel_fabric_profile_parameters = (
        "parcel_fabric",
        "your_parcel_fabric_profile",
    )

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
    def anonymous_agol(cls):
        """Run tests for agol anonymous profile"""
        return cls._get_profile_parameterized_class(
            cls._agol_anonymous_profile_parameters
        )

    @classproperty
    def admin_agol(cls):
        """Run tests for agol admin profile"""
        return cls._get_profile_parameterized_class(cls._agol_admin_profile_parameters)

    @classproperty
    def devext(cls):
        """Run tests for agol profile"""
        return cls._get_profile_parameterized_class(cls._agol_devext_profile_parameters)

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
            cls._agol_admin_profile_parameters,
            cls._enterprise_admin_profile_parameters,
        )

    @classproperty
    def admin_enterprise_and_non_admin_agol(cls):
        """Run tests for admin enterprise and non-admin agol profiles"""
        return cls._get_profile_parameterized_class(
            cls._agol_profile_parameters, cls._enterprise_profile_parameters
        )

    @classproperty
    def enterprise_and_agol_and_agol_dev(cls):
        """Run tests for admin enterprise, prod agol and dev agol profiles"""
        return cls._get_profile_parameterized_class(
            cls._agol_profile_parameters,
            cls._enterprise_admin_profile_parameters,
            cls._agol_devext_profile_parameters,
        )

    @classproperty
    def k8s(cls):
        """Run tests for kubernetes profile"""
        return cls._get_profile_parameterized_class(cls._k8s_profile_parameters)

    @classproperty
    def admin_k8s(cls):
        """Run tests for kubernetes admin profile"""
        return cls._get_profile_parameterized_class(cls._k8s_admin_profile_parameters)

    @classproperty
    def admin_enterprise_and_k8s(cls):
        """Run tests for enterprise admin and kubernetes admin profile"""

        return cls._get_profile_parameterized_class(
            cls._k8s_admin_profile_parameters,
            cls._enterprise_admin_profile_parameters,
        )

    @classproperty
    def all(cls):
        """Run tests for all 3 profiles (agol, enterprise, k8s)"""
        return cls._get_profile_parameterized_class(
            cls._agol_profile_parameters,
            cls._enterprise_profile_parameters,
            cls._k8s_profile_parameters,
        )

    @classproperty
    def admin_all(cls):
        """Run tests for all 3 admin profiles (agol, enterprise, k8s)"""
        return cls._get_profile_parameterized_class(
            cls._agol_admin_profile_parameters,
            cls._enterprise_admin_profile_parameters,
            cls._k8s_admin_profile_parameters,
        )

    @classproperty
    def admin_devent(cls):
        """Run tests for devent admin profile"""
        return cls._get_profile_parameterized_class(
            cls._enterprise_devent_admin_profile_parameters
        )

    @classproperty
    def utility_network(cls):
        """Run tests for utility network profile"""
        return cls._get_profile_parameterized_class(
            cls._utility_network_profile_parameters
        )

    @classproperty
    def workflow_manager(cls):
        """Run tests for utility network profile"""
        return cls._get_profile_parameterized_class(
            cls._workflow_manager_profile_parameters
        )

    @classproperty
    def parcel_fabric(cls):
        """Run tests for utility network profile"""
        return cls._get_profile_parameterized_class(
            cls._parcel_fabric_profile_parameters
        )

    # endregion


class from_to_profiles:
    """
    A set of decorators that inject `from` and `to` profiles into tests.  It will inject a from and to profile into the test.

    Sets the following properties on the test class:
    self.description: the unique description, appended to the test name (e.g. from_agol_to_agol, from_agol_to_enterprise, from_enterprise_to_enterprise)
    self.from_profile: the source profile name
    self.from_gis: the GIS for the source profile, if connection is successful
    self.to_profile: the desination profile name
    self.to_gis: the GIS for the destination profile, if connection is successful
    self.proxies: the detected proxies, if any

    If multiple profiles are injected, the test will be run once for each profile.
    """

    _agol_to_agol_params = {
        "description": "agol_to_agol",
        "from_profile": "your_online_admin_profile",
        "to_profile": "your_online_admin_publication_profile",
    }
    _agol_to_enterprise_params = {
        "description": "agol_to_enterprise",
        "from_profile": "your_online_admin_profile",
        "to_profile": "your_ent_admin_profile",
    }
    _agol_to_k8s_params = {
        "description": "agol_to_k8s",
        "from_profile": "your_online_admin_profile",
        "to_profile": "your_kubernetes_admin_profile",
    }
    _enterprise_to_agol_params = {
        "description": "enterprise_to_agol",
        "from_profile": "your_ent_admin_profile",
        "to_profile": "your_online_admin_profile",
    }
    # TODO Andrew: add another profile if you want these to go to different enterprises
    _enterprise_to_enterprise_params = {
        "description": "enterprise_to_enterprise",
        "from_profile": "your_ent_admin_profile",
        "to_profile": "your_ent_admin_profile",
    }
    _enterprise_to_k8s_params = {
        "description": "enterprise_to_k8s",
        "from_profile": "your_ent_admin_profile",
        "to_profile": "your_kubernetes_admin_profile",
    }
    _k8s_to_agol_params = {
        "description": "k8s_to_agol",
        "from_profile": "your_kubernetes_admin_profile",
        "to_profile": "your_online_admin_profile",
    }
    _k8s_to_enterprise_params = {
        "description": "k8s_to_enterprise",
        "from_profile": "your_kubernetes_admin_profile",
        "to_profile": "your_ent_admin_profile",
    }
    _k8s_to_k8s_params = {
        "description": "k8s_to_k8s",
        "from_profile": "your_kubernetes_admin_profile",
        "to_profile": "your_kubernetes_admin_profile",
    }

    def _get_multi_profile_parameterized_class(*args):
        """Returns a parameterized class for the profile parameters from provided args"""
        # attempt to set gis property constructed from profile
        # in each profile configuration
        _profile_params = []
        for params in [*args]:
            try:
                params["from_gis"] = _get_gis(params["from_profile"])
                params["to_gis"] = _get_gis(params["to_profile"])
                params["proxies"] = PROXIES
            except Exception as e:
                pass
            _profile_params += [params]
        return parameterized_class(
            _profile_params,
            # default test name is {class_name}_{index}_{profile_description}; override to remove index:
            class_name_func=lambda cls, _, param: f"{cls.__name__}_{parameterized.to_safe_name(param['description'])}",
        )

    # region decorators
    @classproperty
    def agol_to_agol(cls):
        """Run tests from agol to agol"""
        return cls._get_multi_profile_parameterized_class(cls._agol_to_agol_params)

    @classproperty
    def agol_to_enterprise(cls):
        """Run tests for agol to enterprise"""
        return cls._get_multi_profile_parameterized_class(
            cls._agol_to_enterprise_params
        )

    @classproperty
    def agol_to_k8s(cls):
        """Run tests for agol to k8s"""
        return cls._get_multi_profile_parameterized_class(cls._agol_to_k8s_params)

    @classproperty
    def enterprise_to_agol(cls):
        """Run tests for enterprise to agol"""
        return cls._get_multi_profile_parameterized_class(
            cls._enterprise_to_agol_params
        )

    @classproperty
    def enterprise_to_enterprise(cls):
        """Run tests for enterprise to enterprise"""
        return cls._get_multi_profile_parameterized_class(
            cls._enterprise_to_enterprise_params
        )

    @classproperty
    def enterprise_to_k8s(cls):
        """Run tests for enterprise to k8s"""
        return cls._get_multi_profile_parameterized_class(cls._enterprise_to_k8s_params)

    @classproperty
    def k8s_to_enterprise(cls):
        """Run tests for k8s to enterprise"""
        return cls._get_multi_profile_parameterized_class(cls._enterprise_to_k8s_params)

    @classproperty
    def k8s_to_agol(cls):
        """Run tests for k8s to agol"""
        return cls._get_multi_profile_parameterized_class(cls._k8s_to_agol_params)

    @classproperty
    def all(cls):
        """Run tests for all from-to profiles"""
        return cls._get_multi_profile_parameterized_class(
            cls._agol_to_agol_params,
            cls._agol_to_enterprise_params,
            cls._agol_to_k8s_params,
            cls._enterprise_to_agol_params,
            cls._enterprise_to_enterprise_params,
            cls._enterprise_to_k8s_params,
            cls._k8s_to_agol_params,
            cls._k8s_to_enterprise_params,
        )

    @classproperty
    def all_except_k8s(cls):
        """Run tests for all from-to profiles, except k8s"""
        return cls._get_multi_profile_parameterized_class(
            cls._agol_to_agol_params,
            cls._agol_to_enterprise_params,
            cls._enterprise_to_agol_params,
            cls._enterprise_to_enterprise_params,
        )

    @classproperty
    def all_except_agol(cls):
        """Run tests for all from-to profiles, except agol"""
        return cls._get_multi_profile_parameterized_class(
            cls._enterprise_to_k8s_params,
            cls._enterprise_to_enterprise_params,
            cls._k8s_to_enterprise_params,
            cls._k8s_to_k8s_params,
        )

    # endregion
