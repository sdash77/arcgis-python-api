import unittest
from arcgis.apps import build_explorer_url

class TestExplorerUrlBuilder(unittest.TestCase):
    """
    Test the creation of app url schemes
    """
    def setUp(self):
        self.item_id = "7584d0ac469748339004a01c80b55fc1"
        self.search = "Portland ME"
        self.bookmark = "Greater Portland, ME"
        self.center = "-123.456,56.987"
        self.scale = 500
        self.wkid = "4326"
        self.rotation = 180
        self.markup = True

    def test_explorer_no_params(self):
        url = build_explorer_url()
        self.assertEqual(url, "https://explorer.arcgis.app")

    def test_navigator_no_params_as_weblink(self):
        self.assertEqual(
            build_explorer_url(url_type="Web"), "https://explorer.arcgis.app"
        )

    def test_navigator_no_params_as_applink(self):
        url = build_explorer_url(url_type="App")
        self.assertEqual(url, "arcgis-explorer://")

    def test_explorer_item_id_as_applink(self):
        url = build_explorer_url(webmap=self.item_id, url_type="App")
        self.assertEqual(url, "arcgis-explorer://?itemID={}".format(self.item_id))

    def test_explorer_item_id_search_as_applink(self):
        url = build_explorer_url(
            webmap=self.item_id, search=self.search, url_type="App"
        )
        self.assertEqual(
            url,
            "arcgis-explorer://?itemID={}&search={}".format(
                self.item_id, "Portland%20ME"
            ),
        )

    def test_explorer_item_id_bookmark_as_applink(self):
        url = build_explorer_url(
            webmap=self.item_id, bookmark=self.bookmark, url_type="App"
        )
        self.assertEqual(
            url,
            "arcgis-explorer://?itemID={}&bookmark={}".format(
                self.item_id, "Greater%20Portland,%20ME"
            ),
        )

    def test_explorer_item_id_center_scale_as_applink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            url_type="App",
        )
        self.assertEqual(
            url,
            "arcgis-explorer://?itemID={}&center={}&scale={}".format(
                self.item_id, self.center, self.scale
            ),
        )

    def test_explorer_item_id_center_scale_wkid_as_weblink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            wkid=self.wkid,
        )
        self.assertEqual(
            url,
            "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}".format(
                self.item_id, self.center, self.scale, self.wkid
            ),
        )

    def test_explorer_item_id_center_scale_rotation_as_weblink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            rotation=self.rotation,
        )
        self.assertEqual(
            url,
            "https://explorer.arcgis.app?itemID={}&center={}&scale={}&rotation={}".format(
                self.item_id, self.center, self.scale, self.rotation
            ),
        )

    def test_explorer_item_id_center_scale_markup_as_weblink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            markup=self.markup,
        )
        self.assertEqual(
            url,
            "https://explorer.arcgis.app?itemID={}&center={}&scale={}&markup={}".format(
                self.item_id, self.center, self.scale, str(self.markup).lower()
                ),
            )

    def test_explorer_item_id_center_scale_wkid_rotation_as_weblink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            wkid=self.wkid,
            rotation=self.rotation,
        )
        self.assertEqual(
            url,
            "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}&rotation={}".format(
                self.item_id, self.center, self.scale, self.wkid, self.rotation
            ),
        )

    def test_explorer_item_id_center_scale_wkid_markup_as_weblink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            wkid=self.wkid,
            markup=self.markup,
        )
        self.assertEqual(
            url,
            "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}&markup={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.wkid,
                str(self.markup).lower(),
            ),
        )

    def test_explorer_item_id_center_scale_wkid_rotation_markup_as_weblink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            wkid=self.wkid,
            rotation=self.rotation,
            markup=self.markup,
        )
        self.assertEqual(
            url,
            "https://explorer.arcgis.app?itemID={}&center={}&scale={}&wkid={}&rotation={}&markup={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.wkid,
                self.rotation,
                str(self.markup).lower(),
            ),
        )

    def test_explorer_item_id_center_scale_rotation_markup_as_weblink(self):
        url = build_explorer_url(
            webmap=self.item_id,
            center=self.center,
            scale=self.scale,
            rotation=self.rotation,
            markup=self.markup,
        )
        self.assertEqual(
            url,
            "https://explorer.arcgis.app?itemID={}&center={}&scale={}&rotation={}&markup={}".format(
                self.item_id,
                self.center,
                self.scale,
                self.rotation,
                str(self.markup).lower(),
            ),
        )

    def test_explorer_exception_incorrect_url_type(self):
        with self.assertRaises(ValueError):
            build_explorer_url(url_type="Fake")

    def test_explorer_exception_no_scale(self):
        with self.assertRaises(ValueError):
            build_explorer_url(webmap=self.item_id, center=self.center)

    def test_explorer_exception_no_item_id_search(self):
        with self.assertRaises(ValueError):
            build_explorer_url(search=self.search)

    def test_explorer_exception_no_item_id_bookmark(self):
        with self.assertRaises(ValueError):
            build_explorer_url(bookmark=self.bookmark)

    def test_explorer_exception_no_item_id_center(self):
        with self.assertRaises(ValueError):
            build_explorer_url(center=self.center)

    def test_explorer_exception_no_item_id_wkid(self):
        with self.assertRaises(ValueError):
            build_explorer_url(wkid=self.wkid)

    def test_explorer_exception_no_item_id_rotation(self):
        with self.assertRaises(ValueError):
            build_explorer_url(rotation=self.rotation)

    def test_explorer_exception_no_item_id_markup(self):
        with self.assertRaises(ValueError):
            build_explorer_url(markup=self.markup)

    def test_explorer_exception_no_center_wkid(self):
        with self.assertRaises(ValueError):
            build_explorer_url(wkid=self.wkid, webmap=self.item_id)

    def test_explorer_exception_no_center_rotation(self):
        with self.assertRaises(ValueError):
            build_explorer_url(rotation=self.rotation, webmap=self.item_id)

    def test_explorer_exception_no_center_markup(self):
        with self.assertRaises(ValueError):
            build_explorer_url(markup=self.markup, webmap=self.item_id)

    def test_explorer_exception_conflicting_params(self):
        with self.assertRaises(ValueError):
            build_explorer_url(
                search=self.search, bookmark=self.bookmark, webmap=self.item_id
            )

    def test_explorer_exception_conflicting_params2(self):
        with self.assertRaises(ValueError):
            build_explorer_url(
                search=self.search,
                center=self.center,
                scale=self.scale,
                webmap=self.item_id,
            )

if __name__ == "__main__":
    unittest.main()

