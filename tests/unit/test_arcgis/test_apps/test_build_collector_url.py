import unittest
import collections
from arcgis.apps import build_collector_url

class TestCollectorUrlBuilder(unittest.TestCase):
    """
    Test the creation of app url schemes
    """
    def setUp(self):
        self.webmap = "7584d0ac469748339004a01c80b55fc1"
        self.center = "-123.456,45.6789"
        self.feature_layer = "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0"

    def test_collector_feature_source_url(self):
        url = build_collector_url(
            webmap=self.webmap, center=self.center, feature_layer=self.feature_layer
        )
        self.assertEqual(
            url,
            "arcgis-collector://?itemID={}&center={}&featureSourceURL={}".format(
                self.webmap,
                self.center,
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0",
            ),
        )

    def test_collector_center(self):
        url = build_collector_url(webmap=self.webmap, center=self.center)
        self.assertEqual(
            url,
            "arcgis-collector://?itemID={}&center={}".format(
                self.webmap, self.center
            ),
        )

    def test_collector_item_id(self):
        url = build_collector_url(webmap=self.webmap)
        self.assertEqual(url, "arcgis-collector://?itemID={}".format(self.webmap))

    def test_collector_no_params(self):
        url = build_collector_url()
        self.assertEqual(url, "arcgis-collector://")

    def test_collector_fields(self):
        url = build_collector_url(
            webmap=self.webmap,
            center=self.center,
            feature_layer=self.feature_layer,
            fields={"name": "test name"},
        )
        self.assertEqual(
            url,
            "arcgis-collector://?itemID={}&center={}&featureSourceURL={}&featureAttributes={}".format(
                self.webmap,
                self.center,
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0",
                "%7B%22name%22:%22test%20name%22%7D",
            ),
        )

    def test_collector_multiple_fields(self):
        url = build_collector_url(
            webmap=self.webmap,
            center=self.center,
            feature_layer=self.feature_layer,
            fields=collections.OrderedDict(
                [("name", "test name"), ("name2", "test name2")]
            ),
        )
        self.assertEqual(
            url,
            "arcgis-collector://?itemID={}&center={}&featureSourceURL={}&featureAttributes={}".format(
                self.webmap,
                self.center,
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0",
                "%7B%22name%22:%22test%20name%22,%22name2%22:%22test%20name2%22%7D",
            ),
        )

    def test_collector_workforce(self):
        url = build_collector_url(
            webmap=self.webmap,
            center="${assignment.latitude},${assignment.longitude}",
            feature_layer=self.feature_layer,
            fields={"address": "${assignment.location}"},
        )
        self.assertEqual(
            url,
            "arcgis-collector://?itemID={}&center={}&featureSourceURL={}&featureAttributes={}".format(
                self.webmap,
                "${assignment.latitude},${assignment.longitude}",
                "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0",
                "%7B%22address%22:%22${assignment.location}%22%7D",
            ),
        )

    def test_collector_exception_no_item_id_center(self):
        with self.assertRaises(ValueError):
            build_collector_url(center=self.center)

    def test_collector_exception_no_item_id_feature_source_url(self):
        with self.assertRaises(ValueError):
            build_collector_url(feature_layer=self.feature_layer)

    def test_collector_exception_no_item_id_fields(self):
        with self.assertRaises(ValueError):
            build_collector_url(fields={"name": "test"})

    def test_collector_exception_no_item_id(self):
        with self.assertRaises(ValueError):
            build_collector_url(center=self.center, fields={"name": "test"})

    def test_collector_exception_no_feature_source_url(self):
        with self.assertRaises(ValueError):
            build_collector_url(webmap=self.webmap, fields={"name": "test"})


if __name__ == "__main__":
    unittest.main()

