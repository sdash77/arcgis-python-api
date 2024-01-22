import unittest
import collections
from arcgis.apps import build_survey123_url

class TestSurvey123UrlBuilder(unittest.TestCase):
    """
    Test the creation of app url schemes
    """
    def setUp(self):
        self.item_id = "7584d0ac469748339004a01c80b55fc1"
        self.center = "-123.456,45.6789"
        self.fields = {"name": "value"}

    def test_survey123_center(self):
        url = build_survey123_url(survey=self.item_id, center=self.center)
        self.assertEqual(
            url,
            "arcgis-survey123://?itemID={}&center={}".format(
                self.item_id, self.center
            ),
        )

    def test_survey123_item_id(self):
        url = build_survey123_url(survey=self.item_id)
        self.assertEqual(url, "arcgis-survey123://?itemID={}".format(self.item_id))

    def test_survey123_no_params(self):
        url = build_survey123_url()
        self.assertEqual(url, "arcgis-survey123://")

    def test_survey123_field(self):
        url = build_survey123_url(
            survey=self.item_id, center=self.center, fields=self.fields
        )
        self.assertEqual(
            url,
            "arcgis-survey123://?itemID={}&center={}&field:{}={}".format(
                self.item_id, self.center, "name", "value"
            ),
        )

    def test_survey123_fields(self):
        url = build_survey123_url(
            survey=self.item_id,
            center=self.center,
            fields=collections.OrderedDict(
                [("name", "value"), ("description", "text")]
            ),
        )
        self.assertEqual(
            url,
            "arcgis-survey123://?itemID={}&center={}&field:{}={}&field:{}={}".format(
                self.item_id, self.center, "name", "value", "description", "text"
            ),
        )

    def test_survey123_workforce(self):
        url = build_survey123_url(
            survey=self.item_id,
            center="${assignment.latitude},${assignment.longitude}",
            fields={"name": "${assignment.description}"},
        )
        self.assertEqual(
            url,
            "arcgis-survey123://?itemID={}&center={}&field:{}".format(
                self.item_id,
                "${assignment.latitude},${assignment.longitude}",
                "name=${assignment.description}",
            ),
        )

    def test_survey123_all(self):
        url = build_survey123_url(
            survey="36ff9e8c13e042a58cfce4ad87f55d19",
            center="37.8199,-122.4783",
            fields={"surname": "Klauser Test"},
        )
        self.assertEqual(
            url,
            "arcgis-survey123://?itemID=36ff9e8c13e042a58cfce4ad87f55d19&center=37.8199,-122.4783&field:surname=Klauser%20Test",
        )

    def test_survey123_exception_no_item_id_center(self):
        with self.assertRaises(ValueError):
            build_survey123_url(center=self.center)

    def test_survey123_exception_no_item_id_fields(self):
        with self.assertRaises(ValueError):
            build_survey123_url(fields={"name": "test"})

    def test_survey123_exception_no_item_id(self):
        with self.assertRaises(ValueError):
            build_survey123_url(center=self.center, fields={"name": "test"})


if __name__ == "__main__":
    unittest.main()
