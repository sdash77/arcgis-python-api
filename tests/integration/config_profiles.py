"""
This configuration file will check and reset all profiles for running gis module integration tests.
If the parameter "reset" for setup_profiles() set as "True", all existing profiles will be reset,
and non-existing profiles will be added.
"""

from enum import Enum
from arcgis.gis import ProfileManager

profile_manager = ProfileManager()


class Credential:
    def __init__(
        self,
        username: str = None,
        password: str = None,
        client_id: str = None,
        key_file: str = None,
        cert_file: str = None,
    ):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.key_file = key_file
        self.cert_file = cert_file

    def __repr__(self):
        props = []
        if self.username:
            props.append(f'username="{self.username}"')
        if self.password:
            props.append('password="*********"')
        if self.client_id:
            props.append(f'client_id="{self.client_id}"')
        if self.key_file:
            props.append(f'key_file="{self.key_file}"')
        if self.cert_file:
            props.append(f'cert_file="{self.cert_file}"')
        return f'Credential({", ".join(props)})'


class PortalType(Enum):
    ONLINE = "online"
    "ArcGIS Online"

    ENTERPRISE = "enterprise"
    "ArcGIS Enterprise"

    ENTERPRISE_K8S = "k8s"
    "ArcGIS Enterprise on Kubernetes"


class PortalEnvironment(Enum):
    PRODUCTION = "production"
    "Currently released production version"

    TESTING = "testing"
    "Version under current development"


class UserType(Enum):
    ADMIN = "admin"
    "Administrator user"

    STANDARD = "standard"
    "Standard user"

    ANONYMOUS = "anonymous"
    "Anonymous user"

    WORKFLOW_MANAGER = "workflow_manager"
    "Workflow Manager user"

    UTILITY_NETWORK = "utility_network"
    "Utility Network user"

    PARCEL_FABRIC = "parcel_fabric"
    "Parcel Fabric user"

    API_DATA_OWNER = "api_data_owner"
    "API Data Owner user"

    ADMIN_PUBLICATION = "admin_publication"
    "Admin Publication user"


class Profile:
    def __init__(
        self,
        name: str,
        verbose_name: str,
        url: str,
        credentials: Credential,
        environment: PortalEnvironment,
        portal_type: PortalType,
        user_type: UserType,
    ):
        self.name = name
        self.verbose_name = verbose_name
        self.url = url
        self.credentials = credentials or Credential()
        self.environment = environment
        self.portal_type = portal_type
        self.user_type = user_type

    def __repr__(self):
        return f'Profile(name="{self.name}", verbose_name="{self.verbose_name}", url="{self.url}", credentials={self.credentials}, environment={self.environment}, portal_type={self.portal_type}, user_type={self.user_type})'


class Profiles:
    _profiles = {
        PortalEnvironment.PRODUCTION: {
            PortalType.ENTERPRISE: {
                UserType.ADMIN: Profile(
                    name="your_ent_admin_profile",
                    verbose_name="your_prod_ent_admin_profile",
                    url="https://pythonapitestnb.dev.geocloud.com/portal/",
                    credentials=Credential(
                        username="arcgispyapibot", password="geosaurus_automation123"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.ADMIN,
                ),
                UserType.STANDARD: Profile(
                    name="your_enterprise_profile",
                    verbose_name="your_prod_enterprise_profile",
                    url="https://pythonapitestnb.dev.geocloud.com/portal/",
                    credentials=Credential(
                        username="arcgis_python", password="amazing_arcgis_123"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.STANDARD,
                ),
                UserType.WORKFLOW_MANAGER: Profile(
                    name="your_workflow_manager_profile",
                    verbose_name="your_prod_workflow_manager_profile",
                    url="https://mcstest165.esri.com/portal",
                    credentials=Credential(username="admin", password="esri.agp"),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.WORKFLOW_MANAGER,
                ),
                UserType.UTILITY_NETWORK: Profile(
                    name="your_utility_network_profile",
                    verbose_name="your_prod_utility_network_profile",
                    url="https://utilitynetwork.esri.com/portal",
                    credentials=Credential(
                        username="python_api_team", password="python_api_team.109"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.UTILITY_NETWORK,
                ),
                UserType.PARCEL_FABRIC: Profile(
                    name="your_parcel_fabric_profile",
                    verbose_name="your_prod_parcel_fabric_profile",
                    url="https://dev0016752.esri.com/portal",
                    credentials=Credential(username="admin", password="esri.agp"),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.PARCEL_FABRIC,
                ),
            },
            PortalType.ENTERPRISE_K8S: {
                UserType.ADMIN: Profile(
                    name="your_kubernetes_admin_profile",
                    verbose_name="your_prod_kubernetes_admin_profile",
                    url="https://1150pubbi-1150pubbi.apps.openshift416release.esri.com/web",
                    credentials=Credential(
                        username="PAPIadmin", password="PAPIletmein01"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ENTERPRISE_K8S,
                    user_type=UserType.ADMIN,
                ),
                UserType.STANDARD: Profile(
                    name="your_kubernetes_profile",
                    verbose_name="your_prod_kubernetes_profile",
                    url="https://1150pubbi-1150pubbi.apps.openshift416release.esri.com/web",
                    credentials=Credential(
                        username="PAPIpublisher", password="PAPIletmein01"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ENTERPRISE_K8S,
                    user_type=UserType.STANDARD,
                ),
            },
            PortalType.ONLINE: {
                UserType.ADMIN: Profile(
                    name="your_online_admin_profile",
                    verbose_name="your_prod_online_admin_profile",
                    url="https://www.arcgis.com",
                    credentials=Credential(
                        username="arcgispyapibot", password="geosaurus_automation123"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ONLINE,
                    user_type=UserType.ADMIN,
                ),
                UserType.STANDARD: Profile(
                    name="your_online_profile",
                    verbose_name="your_prod_online_profile",
                    url="https://www.arcgis.com",
                    credentials=Credential(
                        username="arcgis_python", password="amazing_arcgis_123"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ONLINE,
                    user_type=UserType.STANDARD,
                ),
                UserType.ANONYMOUS: Profile(
                    name="your_anonymous_online_profile",
                    verbose_name="your_prod_anonymous_online_profile",
                    url="https://www.arcgis.com",
                    credentials=None,
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ONLINE,
                    user_type=UserType.ANONYMOUS,
                ),
                UserType.API_DATA_OWNER: Profile(
                    name="your_online_api_data_owner_profile",
                    verbose_name="your_prod_online_api_data_owner_profile",
                    url="https://www.arcgis.com",
                    credentials=Credential(
                        username="api_data_owner", password="donot3xposeme"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ONLINE,
                    user_type=UserType.API_DATA_OWNER,
                ),
                UserType.ADMIN_PUBLICATION: Profile(
                    name="your_online_admin_publication_profile",
                    verbose_name="your_prod_online_admin_publication_profile",
                    url="https://pythonapi.maps.arcgis.com",
                    credentials=Credential(
                        username="python_api_test", password="esri.agp2"
                    ),
                    environment=PortalEnvironment.PRODUCTION,
                    portal_type=PortalType.ONLINE,
                    user_type=UserType.ADMIN_PUBLICATION,
                ),
            },
        },
        PortalEnvironment.TESTING: {
            PortalType.ENTERPRISE: {
                # TODO these credentials are for k8s, need to update for non-k8s enterprise
                UserType.ADMIN: Profile(
                    name="your_ent_admin_profile",
                    verbose_name="your_dev_ent_admin_profile",
                    url="https://devent.esri.com/gis",
                    credentials=Credential(
                        username="administrator", password="esri.agp1"
                    ),
                    environment=PortalEnvironment.TESTING,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.ADMIN,
                ),
                UserType.STANDARD: Profile(
                    name="your_enterprise_profile",
                    verbose_name="your_dev_enterprise_profile",
                    url="https://devent.esri.com/gis",
                    credentials=Credential(
                        username="pythonapiuser", password="geosaurus_automation123"
                    ),
                    environment=PortalEnvironment.TESTING,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.STANDARD,
                ),
            },
            PortalType.ENTERPRISE_K8S: {
                UserType.ADMIN: Profile(
                    name="your_kubernetes_admin_profile",
                    verbose_name="your_dev_kubernetes_admin_profile",
                    url="https://rqa01bi-rqa01bi.apps.openshift416release.esri.com/gis",
                    credentials=Credential(
                        username="PAPIadmin", password="PAPIletmein01"
                    ),
                    environment=PortalEnvironment.TESTING,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.ADMIN,
                ),
                UserType.STANDARD: Profile(
                    name="your_kubernetes_profile",
                    verbose_name="your_dev_kubernetes_profile",
                    url="https://rqa01bi-rqa01bi.apps.openshift416release.esri.com/gis",
                    credentials=Credential(
                        username="PAPIpublisher", password="PAPIletmein01"
                    ),
                    environment=PortalEnvironment.TESTING,
                    portal_type=PortalType.ENTERPRISE,
                    user_type=UserType.STANDARD,
                ),
            },
            PortalType.ONLINE: {
                UserType.ADMIN: Profile(
                    name="your_dev_online_profile",
                    verbose_name="your_dev_online_admin_profile",
                    url="https://devgeosaurus.mapsdevext.arcgis.com",
                    credentials=Credential(
                        username="esrirequests", password="portalaccount1"
                    ),
                    environment=PortalEnvironment.TESTING,
                    portal_type=PortalType.ONLINE,
                    user_type=UserType.ADMIN,
                ),
                UserType.STANDARD: Profile(
                    name="your_online_profile",
                    verbose_name="your_dev_online_profile",
                    url="https://devgeosaurus.mapsdevext.arcgis.com",
                    credentials=Credential(
                        username="arcgis_python", password="amazing_arcgis_123"
                    ),
                    environment=PortalEnvironment.TESTING,
                    portal_type=PortalType.ONLINE,
                    user_type=UserType.STANDARD,
                ),
            },
        },
    }

    @classmethod
    def all(cls, environment: PortalEnvironment | None = None) -> list[Profile]:
        return [
            profile
            for env, portal_types in cls._profiles.items()
            if environment is None or env == environment
            for _, user_types in portal_types.items()
            for _, profile in user_types.items()
        ]

    @classmethod
    def all_names(cls, environment: PortalEnvironment | None = None) -> set[str]:
        return {profile.name for profile in cls.all(environment=environment)} | {
            profile.verbose_name for profile in cls.all(environment=environment)
        }

    @classmethod
    def get(
        cls,
        environment: PortalEnvironment = PortalEnvironment.PRODUCTION,
        portal_type: PortalType = PortalType.ENTERPRISE,
        user_type: UserType = UserType.STANDARD,
    ) -> Profile | None:
        """Get a profile by environment, portal type, and user type."""
        return cls._profiles.get(environment, {}).get(portal_type, {}).get(user_type)

    @classmethod
    def configure_all(
        cls, environment: PortalEnvironment = PortalEnvironment.PRODUCTION
    ):
        installed_profiles = set(profile_manager.list())
        for profile in cls.all():
            # always insert verbose name
            # e.g. your_prod_ent_admin_profile
            names = [profile.verbose_name]
            if profile.environment == environment:
                # also insert name if it matches the current environment
                # e.g. your_ent_admin_profile if requested to seed profiles for production
                names.append(profile.name)
            for name in names:
                if name in installed_profiles:
                    print(f"Profile already configured: {name}")
                    continue
                profile_manager.create(
                    name,
                    profile.url,
                    username=profile.credentials.username,
                    password=profile.credentials.password,
                    client_id=profile.credentials.client_id,
                    key_file=profile.credentials.key_file,
                    cert_file=profile.credentials.cert_file,
                )
                print(f"Configured profile: {name}")


def setup_profiles(
    environment: PortalEnvironment = PortalEnvironment.PRODUCTION,
    reset=False,
):
    """create profiles"""

    # remove profiles if they already exist
    if reset is True:
        installed_profiles = set(profile_manager.list())
        print("Reset=True: Removing existing profiles...")
        for profile in Profiles.all_names():
            if profile in installed_profiles:
                profile_manager.delete(profile)
                print(f"Deleted profile: {profile}")

    Profiles.configure_all(environment=environment)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure GIS login profiles for integration testing"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--test",
        dest="environment",
        action="store_const",
        const=PortalEnvironment.TESTING,
        default=PortalEnvironment.PRODUCTION,
        help="Use testing environment profiles",
    )
    group.add_argument(
        "--prod",
        dest="environment",
        action="store_const",
        const=PortalEnvironment.PRODUCTION,
        help="Use production environment profiles (default)",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not reset the profiles; if provided, existing profiles matching the seed profile names will not be destroyed",
    )
    args = parser.parse_args()
    setup_profiles(
        environment=PortalEnvironment(args.environment), reset=not args.no_reset
    )
