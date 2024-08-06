import unittest
from arcgis.apps import build_navigator_url

class TestNavigatorUrlBuilder(unittest.TestCase):
    """
    Test the creation of app url schemes
    """
    def test_navigator_no_params(self):
        self.assertEqual(build_navigator_url(), "https://navigator.arcgis.app")

    def test_navigator_no_params_as_weblink(self):
        self.assertEqual(
            build_navigator_url(url_type="Web"), "https://navigator.arcgis.app"
        )

    def test_navigator_no_params_as_applink(self):
        url = build_navigator_url(url_type="App")
        self.assertEqual(url, "arcgis-navigator://")

    def test_navigator_one_stop_with_non_name_as_applink(self):
        stop = ("-123.456,67.87",)
        url = build_navigator_url(stops=[stop], url_type="App")
        self.assertEqual(
            url, "arcgis-navigator://?stop={}".format("-123.456,67.87")
        )

    def test_navigator_one_stop_with_name_as_applink(self):
        stop = ("-123.456,67.87", "esri")
        url = build_navigator_url(stops=[stop], url_type="App")
        self.assertEqual(
            url,
            "arcgis-navigator://?stop={}&stopname={}".format(
                "-123.456,67.87", stop[1]
            ),
        )

    def test_navigator_one_stop_with_name_as_applink_with_webmap(self):
        stop = ("-123.456,67.87", "esri")
        url = build_navigator_url(
            stops=[stop], url_type="App", webmap="da5fdb60b7854b2881f80e275bb802da"
        )
        self.assertEqual(
            url,
            "arcgis-navigator://?itemID={}&stop={}&stopname={}".format(
                "da5fdb60b7854b2881f80e275bb802da", "-123.456,67.87", stop[1]
            ),
        )

    def test_navigator_two_stops_with_names_as_applink(self):
        stops = [
            ("-123.456,67.87", "esri office"),
            ("-123.654,34.45", "portland maine"),
        ]
        url = build_navigator_url(stops=stops, url_type="App")
        self.assertEqual(
            url,
            "arcgis-navigator://?stop={}&stopname={}&stop={}&stopname={}".format(
                "-123.456,67.87",
                "esri%20office",
                "-123.654,34.45",
                "portland%20maine",
            ),
        )

    def test_navigator_two_stops_one_name_as_applink(self):
        stops = [("-123.456,67.87", "esri"), ("-123.654,34.45",)]
        url = build_navigator_url(stops=stops, url_type="App")
        self.assertEqual(
            url,
            "arcgis-navigator://?stop={}&stopname={}&stop={}".format(
                "-123.456,67.87", "esri", "-123.654,34.45"
            ),
        )

    def test_navigator_two_stops_no_names_as_applink(self):
        stops = [("-123.456,67.87",), ("-123.654,34.45",)]
        url = build_navigator_url(stops=stops, url_type="App")
        self.assertEqual(
            url,
            "arcgis-navigator://?stop={}&stop={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
            ),
        )

    def test_navigator_two_stops_optimize_as_applink(self):
        stops = [("-123.456,67.87",), ("-123.654,34.45",)]
        url = build_navigator_url(stops=stops, optimize=True, url_type="App")
        self.assertEqual(
            url,
            "arcgis-navigator://?stop={}&stop={}&optimize={}".format(
                "-123.456,67.87", "-123.654,34.45", "true"
            ),
        )

    def test_navigator_two_stops_navigate_as_weblink(self):
        stops = [("-123.456,67.87",), ("-123.654,34.45",)]
        url = build_navigator_url(stops=stops, navigate=True)
        self.assertEqual(
            url,
            "https://navigator.arcgis.app?stop={}&stop={}&navigate={}".format(
                "-123.456,67.87", "-123.654,34.45", "true"
            ),
        )

    def test_navigator_two_stops_navigate_optimize_as_weblink(self):
        stops = [("-123.456,67.87",), ("-123.654,34.45",)]
        url = build_navigator_url(stops=stops, navigate=True, optimize=True)
        self.assertEqual(
            url,
            "https://navigator.arcgis.app?stop={}&stop={}&optimize={}&navigate={}".format(
                "-123.456,67.87", "-123.654,34.45", "true", "true"
            ),
        )

    def test_navigator_two_stops_callback_as_weblink(self):
        stops = [("-123.456,67.87",), ("-123.654,34.45",)]
        url = build_navigator_url(
            stops=stops,
            callback="arcgis-collector://",
            callback_prompt="Collector for ArcGIS",
        )
        self.assertEqual(
            url,
            "https://navigator.arcgis.app?stop={}&stop={}&callback={}&callbackprompt={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
                "arcgis-collector://",
                "Collector%20for%20ArcGIS",
            ),
        )

    def test_navigator_two_stops_callback_no_prompt_as_weblink(self):
        stops = [("-123.456,67.87",), ("-123.654,34.45",)]
        url = build_navigator_url(stops=stops, callback="arcgis-collector://")
        self.assertEqual(
            url,
            "https://navigator.arcgis.app?stop={}&stop={}&callback={}".format(
                "-123.456,67.87", "-123.654,34.45", "arcgis-collector://"
            ),
        )

    def test_navigator_two_stops_travel_mode_as_weblink(self):
        stops = [("-123.456,67.87",), ("-123.654,34.45",)]
        url = build_navigator_url(stops=stops, travel_mode="Driving Time")
        self.assertEqual(
            url,
            "https://navigator.arcgis.app?stop={}&stop={}&travelmode={}".format(
                "-123.456,67.87", "-123.654,34.45", "Driving%20Time"
            ),
        )

    def test_navigator_two_stops_custom_travel_mode_as_weblink(self):
        stops = ["-123.456,67.87", "-123.654,34.45"]
        url = build_navigator_url(stops=stops, travel_mode="Custom Driving Time")
        self.assertEqual(
            url,
            "https://navigator.arcgis.app?stop={}&stop={}&travelmode={}".format(
                "-123.456,67.87", "-123.654,34.45", "Custom%20Driving%20Time"
            ),
        )

    def test_navigator_stop_with_no_name_as_weblink(self):
        stops = ["-123.456,67.87", "-123.654,34.45"]
        url = build_navigator_url(stops=stops)
        self.assertEqual(
            url,
            "https://navigator.arcgis.app?stop={}&stop={}".format(
                "-123.456,67.87",
                "-123.654,34.45",
            ),
        )

    def test_navigator_exception_incorrect_url_type(self):
        with self.assertRaises(ValueError):
            build_navigator_url(url_type="Fake")

    def test_navigator_navigate_no_stops(self):
        with self.assertRaises(ValueError):
            build_navigator_url(navigate=True)

    def test_navigator_optimize_no_stops(self):
        with self.assertRaises(ValueError):
            build_navigator_url(optimize=True)

    def test_navigator_travel_mode_no_stops(self):
        with self.assertRaises(ValueError):
            build_navigator_url(travel_mode="Driving Time")

    def test_navigator_callback_no_stops(self):
        with self.assertRaises(ValueError):
            build_navigator_url(callback="arcgis-collector://")


if __name__ == "__main__":
    unittest.main()

