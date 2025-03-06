import unittest
import uuid
from utils.decorators import integration_test, profiles
from arcgis.gis import GIS, ItemProperties, ItemTypeEnum
import datetime as _dt


@integration_test
@profiles.admin_agol
class TestDeveloperCredentials(unittest.TestCase):
    def test_create_developer_credentials(self):
        folder = self.gis.content.folders.get()
        expiration = _dt.datetime(2025, 7, 1)
        item_properties: dict = {
            "typeKeywords": [],
            "type": "Application",
            "apiToken1ExpirationDate": int(expiration.timestamp() * 1000),
            "title": "My First Developer Token",
            "subscriptionType": "app",
            "isPersonalAPIToken": True,
            "tags": "ntgrtn-tst",
        }
        item = folder.add(item_properties=item_properties).result()

        privileges = [
            "premium:user:basemaps",
            "premium:user:geocode",
            "premium:user:networkanalysis",
            "premium:user:geoenrichment",
            "portal:user:viewOrgUsers",
            "portal:user:createGroup",
            "portal:user:joinGroup",
            "portal:user:joinNonOrgGroup",
            "portal:user:viewOrgGroups",
            "portal:user:invitePartneredCollaborationMembers",
            "portal:user:addExternalMembersToGroup",
            "portal:user:createItem",
            "portal:publisher:publishFeatures",
            "portal:publisher:publishTiles",
            "portal:publisher:publishScenes",
            "portal:publisher:publishTiledImagery",
            "portal:publisher:publishDynamicImagery",
            "portal:user:viewOrgItems",
            "premium:publisher:createNotebooks",
            "premium:publisher:scheduleNotebooks",
            "portal:user:viewTracks",
            "portal:user:reassignItems",
            "portal:publisher:createDataPipelines",
            "portal:user:shareToGroup",
            "portal:user:shareToOrg",
            "portal:user:shareToPublic",
            "portal:user:shareGroupToOrg",
            "portal:user:shareGroupToPublic",
            "premium:publisher:createAdvancedNotebooks",
            "premium:user:demographics",
            "premium:user:featurereport",
            "features:user:edit",
            "features:user:fullEdit",
            "premium:user:spatialanalysis",
            "premium:publisher:rasteranalysis",
            "portal:admin:viewUsers",
            "portal:admin:updateUsers",
            "portal:admin:deleteUsers",
            "portal:admin:inviteUsers",
            "portal:admin:disableUsers",
            "portal:admin:changeUserRoles",
            "portal:admin:manageLicenses",
            "portal:admin:updateMemberCategorySchema",
            "portal:admin:viewGroups",
            "portal:admin:updateGroups",
            "portal:admin:deleteGroups",
            "portal:admin:reassignGroups",
            "portal:admin:assignToGroups",
            "portal:admin:manageEnterpriseGroups",
            "portal:admin:createUpdateCapableGroup",
            "portal:admin:createLeavingDisallowedGroup",
            "portal:admin:viewItems",
            "portal:admin:updateItems",
            "portal:admin:deleteItems",
            "portal:admin:reassignItems",
            "portal:admin:updateItemCategorySchema",
            "portal:publisher:publishServerGPServices",
            "portal:admin:shareToOrg",
            "portal:admin:shareToPublic",
            "portal:admin:createReports",
            "portal:admin:manageSecurity",
            "portal:admin:manageWebsite",
            "portal:admin:manageCollaborations",
            "portal:admin:manageCredits",
            "portal:admin:manageRoles",
            "portal:admin:manageUtilityServices",
        ]
        registration_app_info = item.register(
            app_type='multiple',
            redirect_uris=["urn:ietf:wg:oauth:2.0:oob"],
            http_referers=['http'],
            privileges=privileges,
            personal_token=True,
        )
        registration_app_info
        expiration = _dt.datetime(2025, 7, 1)

        token_info: dict = item.generate_api_token(
            slot=1,
            regenerate=False,
            expiration=_dt.datetime.now() + _dt.timedelta(weeks=30),
        )
        assert token_info.get("access_token")
        assert GIS(
            url=self.gis.resturl,
            token=token_info['access_token'],
            set_active=False,
            verify_cert=False,
            trust_env=True,
        ).properties['appInfo']
        item.delete(permanent=True)

    def test_regenerate_developer_credentials(self):
        folder = self.gis.content.folders.get()
        expiration = _dt.datetime(2025, 7, 1)
        item_properties: dict = {
            "typeKeywords": [],
            "type": "Application",
            "apiToken1ExpirationDate": int(expiration.timestamp() * 1000),
            "title": "My First Developer Token",
            "subscriptionType": "app",
            "isPersonalAPIToken": True,
            "tags": "ntgrtn-tst",
        }
        item = folder.add(item_properties=item_properties).result()

        privileges = [
            "premium:user:basemaps",
            "premium:user:geocode",
            "premium:user:networkanalysis",
            "premium:user:geoenrichment",
            "portal:user:viewOrgUsers",
            "portal:user:createGroup",
            "portal:user:joinGroup",
            "portal:user:joinNonOrgGroup",
            "portal:user:viewOrgGroups",
            "portal:user:invitePartneredCollaborationMembers",
            "portal:user:addExternalMembersToGroup",
            "portal:user:createItem",
            "portal:publisher:publishFeatures",
            "portal:publisher:publishTiles",
            "portal:publisher:publishScenes",
            "portal:publisher:publishTiledImagery",
            "portal:publisher:publishDynamicImagery",
            "portal:user:viewOrgItems",
            "premium:publisher:createNotebooks",
            "premium:publisher:scheduleNotebooks",
            "portal:user:viewTracks",
            "portal:user:reassignItems",
            "portal:publisher:createDataPipelines",
            "portal:user:shareToGroup",
            "portal:user:shareToOrg",
            "portal:user:shareToPublic",
            "portal:user:shareGroupToOrg",
            "portal:user:shareGroupToPublic",
            "premium:publisher:createAdvancedNotebooks",
            "premium:user:demographics",
            "premium:user:featurereport",
            "features:user:edit",
            "features:user:fullEdit",
            "premium:user:spatialanalysis",
            "premium:publisher:rasteranalysis",
            "portal:admin:viewUsers",
            "portal:admin:updateUsers",
            "portal:admin:deleteUsers",
            "portal:admin:inviteUsers",
            "portal:admin:disableUsers",
            "portal:admin:changeUserRoles",
            "portal:admin:manageLicenses",
            "portal:admin:updateMemberCategorySchema",
            "portal:admin:viewGroups",
            "portal:admin:updateGroups",
            "portal:admin:deleteGroups",
            "portal:admin:reassignGroups",
            "portal:admin:assignToGroups",
            "portal:admin:manageEnterpriseGroups",
            "portal:admin:createUpdateCapableGroup",
            "portal:admin:createLeavingDisallowedGroup",
            "portal:admin:viewItems",
            "portal:admin:updateItems",
            "portal:admin:deleteItems",
            "portal:admin:reassignItems",
            "portal:admin:updateItemCategorySchema",
            "portal:publisher:publishServerGPServices",
            "portal:admin:shareToOrg",
            "portal:admin:shareToPublic",
            "portal:admin:createReports",
            "portal:admin:manageSecurity",
            "portal:admin:manageWebsite",
            "portal:admin:manageCollaborations",
            "portal:admin:manageCredits",
            "portal:admin:manageRoles",
            "portal:admin:manageUtilityServices",
        ]
        registration_app_info = item.register(
            app_type='multiple',
            redirect_uris=["urn:ietf:wg:oauth:2.0:oob"],
            http_referers=['http'],
            privileges=privileges,
            personal_token=True,
        )
        registration_app_info
        expiration = _dt.datetime(2025, 7, 1)

        token_info: dict = item.generate_api_token(
            slot=1,
            regenerate=False,
            expiration=_dt.datetime.now() + _dt.timedelta(weeks=30),
        )
        r = token_info.get("access_token")
        token_info: dict = item.generate_api_token(
            slot=1,
            regenerate=False,
            expiration=_dt.datetime.now() + _dt.timedelta(weeks=30),
        )
        r1 = token_info.get("access_token")
        assert r != r1

        item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
