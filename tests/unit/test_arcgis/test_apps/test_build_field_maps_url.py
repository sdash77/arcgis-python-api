import unittest
from arcgis.apps import build_field_maps_url

class TestFieldMapsUrlBuilder(unittest.TestCase):
    """
    Test the creation of app url schemes
    """
    def setUp(self):
        self.portal_url = "https://rags19003.ags.esri.com/portal"
        self.webmap = "7584d0ac469748339004a01c80b55fc1"
        self.center = "41.780618,-88.179449"
        self.center_address = "100 Commercial St, Portland, ME 04101"
        self.scale = 3000
        self.bookmark = "Esri Portland Office"
        self.wkid = 4326
        self.search = "75 Washington Ave, Portland, ME 04101"
        self.geometry = {
            "rings": [
                [
                    [-117.1961714, 34.0547155],
                    [-117.1961714, 34.0587155],
                    [-117.2001714, 34.0587155],
                    [-117.2001714, 34.0547155],
                ]
            ],
            "spatialReference": {"wkid": 4326},
        }
        self.feature_layer = "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0"
        self.fields = {"name": "Mayor of Portland"}
        self.feature_id = "0000000-0000-0000-0000-0000000000000"
        self.callback = "arcgis-explorer://"
        self.callback_prompt = "Explore At Location"


    def test_field_maps_open_map(self):
        url = build_field_maps_url(webmap=self.webmap, action="open")
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext={}&itemID={}".format(
                "open",
                self.webmap,
            ),
        )

    def test_field_maps_only_portal(self):
        url = build_field_maps_url(portal=self.portal_url)
        self.assertEqual(
            url, "https://fieldmaps.arcgis.app?portalURL={}".format(self.portal_url)
        )

    def test_field_maps_portal_url(self):
        url = build_field_maps_url(
            webmap=self.webmap, portal=self.portal_url, action="open"
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?portalURL={}&referenceContext={}&itemID={}".format(
                self.portal_url, "open", self.webmap
            ),
        )

    def test_field_maps_center_scale_map(self):
        url = build_field_maps_url(
            action="center",
            webmap=self.webmap,
            center=[41.780618, -88.179449],
            scale=self.scale,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=center&itemID={}&scale={}&center={}".format(
                self.webmap, self.scale, self.center
            ),
        )

    def test_field_maps_center_scale_map_wkid(self):
        url = build_field_maps_url(
            action="center",
            webmap=self.webmap,
            center="41.780618,-88.179449",
            scale=self.scale,
            wkid=self.wkid,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=center&itemID={}&scale={}&wkid={}&center={}".format(
                self.webmap, self.scale, self.wkid, self.center
            ),
        )

    def test_field_maps_center_geocoded_address(self):
        url = build_field_maps_url(
            action="center",
            webmap=self.webmap,
            center=self.center_address,
            scale=self.scale,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=center&itemID={}&scale={}&center={}".format(
                self.webmap, self.scale, "100+Commercial+St,+Portland,+ME+04101"
            ),
        )

    def test_field_maps_search_address(self):
        url = build_field_maps_url(
            action="search", webmap=self.webmap, search=self.search
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=search&itemID={}&search={}".format(
                self.webmap, "75+Washington+Ave,+Portland,+ME+04101"
            ),
        )

    def test_field_maps_search_asset(self):
        url = build_field_maps_url(
            webmap=self.webmap, action="search", search=43141
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=search&itemID={}&search={}".format(
                self.webmap, "43141"
            ),
        )

    def test_field_maps_view_bookmark(self):
        url = build_field_maps_url(
            webmap=self.webmap, action="open", bookmark=self.bookmark
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=open&itemID={}&bookmark={}".format(
                self.webmap, "Esri+Portland+Office"
            ),
        )

    def test_field_maps_initiate_capture(self):
        url = build_field_maps_url(
            webmap=self.webmap,
            action="addFeature",
            feature_layer=self.feature_layer,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=addFeature&itemID={}&featureSourceURL={}".format(
                self.webmap, self.feature_layer
            ),
        )

    def test_field_maps_initiate_capture_with_geometry(self):
        url = build_field_maps_url(
            webmap=self.webmap,
            action="addFeature",
            feature_layer=self.feature_layer,
            geometry=self.geometry,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=addFeature"
            "&itemID=7584d0ac469748339004a01c80b55fc1"
            "&featureSourceURL=https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0"
            "&geometry={%22rings%22:%5B%5B%5B-117.1961714,34.0547155%5D,%5B-117.1961714,34.0587155%5D,%5B-117.2001714,34.0587155%5D,%5B-117.2001714,34.0547155%5D%5D%5D,%22spatialReference%22:{%22wkid%22:4326}}",
        )

    def test_field_maps_use_antenna(self):
        url = build_field_maps_url(
            webmap=self.webmap,
            action="addFeature",
            use_antenna_height=True,
            use_loc_profile=True,
            geometry="34.058030,-117.195940, 1200",
            feature_layer=self.feature_layer,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=addFeature&itemID={}&featureSourceURL={}"
            "&geometry=34.058030,-117.195940,1200&useAntennaHeight=true&useLocationProfile=true".format(
                self.webmap, self.feature_layer
            ),
        )

    def test_field_maps_callback(self):
        url = build_field_maps_url(
            webmap=self.webmap,
            action="addFeature",
            feature_layer=self.feature_layer,
            callback=self.callback,
            callback_prompt=self.callback_prompt,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=addFeature&itemID={}"
            "&featureSourceURL={}&callback={}&callbackPrompt={}".format(
                self.webmap,
                self.feature_layer,
                self.callback,
                "Explore%20At%20Location",
            ),
        )

    def test_field_maps_update_feature(self):
        url = build_field_maps_url(
            webmap=self.webmap,
            action="updateFeature",
            feature_layer=self.feature_layer,
            feature_id=self.feature_id,
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=updateFeature&itemID={}"
            "&featureSourceURL={}&featureID={}".format(
                self.webmap, self.feature_layer, self.feature_id
            ),
        )

    def test_field_maps_anonymous(self):
        url = build_field_maps_url(
            webmap=self.webmap, action="open", anonymous=True
        )
        self.assertEqual(
            url,
            "https://fieldmaps.arcgis.app?referenceContext=open&itemID={}"
            "&anonymousAccess=true".format(
                self.webmap,
            ),
        )

    def test_field_maps_url_bad_action(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="blah")

    def test_field_maps_url_no_action(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(webmap=self.webmap)

    def test_field_maps_url_invalid_webmap(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="center", webmap=123)

    def test_field_maps_search_without_webmap(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="search", search="100 Commercial St")

    def test_field_maps_bookmark_without_webmap(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="open", bookmark="100 Commercial St")

    def test_field_maps_center_without_webmap(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="center", center="100 Commercial St")

    def test_field_maps_invalid_scale(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="center", scale=123)

    def test_field_maps_wkid_without_center(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="center", webmap=self.webmap, wkid=4326)

    def test_field_maps_invalid_wkid(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(
                action="center",
                webmap=self.webmap,
                center="100 Commercial St",
                wkid="4326",
            )

    def test_field_maps_feature_layer_bad_action(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(
                action="open", webmap=self.webmap, feature_layer=self.feature_layer
            )

    def test_field_maps_fields_without_feature_layer(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(
                action="addFeature",
                webmap=self.webmap,
                fields={"name": "John Smith"},
            )

    def test_field_maps_geometry_without_feature_layer(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(
                action="addFeature", webmap=self.webmap, geometry=self.geometry
            )

    def test_field_maps_use_antenna_height_without_feature_layer(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(
                action="addFeature",
                webmap=self.webmap,
                geometry=self.geometry,
                use_antenna_height=True,
            )

    def test_field_maps_use_location_profile_bad_action(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(
                action="open",
                webmap=self.webmap,
                geometry=self.geometry,
                use_loc_profile=True,
                feature_layer=self.feature_layer,
            )

    def test_field_maps_feature_id_bad_action(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(
                action="addFeature", webmap=self.webmap, feature_id=self.feature_id
            )

    def test_field_maps_callback_without_webmap(self):
        with self.assertRaises(ValueError):
            build_field_maps_url(action="addFeature", callback=self.callback)


if __name__ == "__main__":
    unittest.main()
