import unittest
from arcgis.map import Map
from arcgis.map._basemap_styles_service import (
    BasemapStylesService,
    BasemapStyle,
    BasemapStylesLanguage,
    BasemapStylesPlace,
    BasemapStylesWorldview,
)
from utils.decorators import integration_test, profiles


# This is only available for online and location platform as of R2.2025
@profiles.agol
@integration_test
class TestAddLayersToMap(unittest.TestCase):

    def setUp(self):
        # create webmap
        self.wm = Map(gis=self.gis)
        assert isinstance(self.wm, Map)

    def test_basemap_styles_service(self):
        """
        Test adding a basemap styles service to the map.
        """
        # Add a basemap styles service
        basemap_styles_service = self.wm.basemap.basemap_styles_service
        assert isinstance(basemap_styles_service, BasemapStylesService)

        # Get list of all basemap styles
        styles = basemap_styles_service.styles
        assert isinstance(styles, list)
        assert isinstance(styles[0], BasemapStyle)

        # Check properties of the first style
        first_style = styles[0]
        assert isinstance(first_style.language, BasemapStylesLanguage)
        assert isinstance(first_style.place, BasemapStylesPlace)
        assert isinstance(first_style.worldview, BasemapStylesWorldview)

        # Get Style names
        style_name = basemap_styles_service.styles_names
        assert isinstance(style_name, list)
        assert isinstance(style_name[0], str)

    def test_basemap_styles_service_language(self):
        """
        Test getting the language of a basemap style.
        """
        basemap_styles_service = self.wm.basemap.basemap_styles_service
        styles = basemap_styles_service.styles
        first_style = styles[0]

        # Check the language property
        assert isinstance(first_style.language, BasemapStylesLanguage)
        # Set the language to 'fr'
        first_style.language = BasemapStylesLanguage.FRENCH
        assert first_style.language == BasemapStylesLanguage.FRENCH

    def test_basemap_styles_service_place(self):
        """
        Test getting the place of a basemap style.
        """
        basemap_styles_service = self.wm.basemap.basemap_styles_service
        styles = basemap_styles_service.styles
        first_style = styles[0]

        # Check the place property
        assert isinstance(first_style.place, BasemapStylesPlace)
        # Set the place to 'us'
        first_style.place = BasemapStylesPlace.ALL
        assert first_style.place == BasemapStylesPlace.ALL

    def test_basemap_styles_service_worldview(self):
        """
        Test getting the worldview of a basemap style.
        """
        basemap_styles_service = self.wm.basemap.basemap_styles_service
        styles = basemap_styles_service.styles
        first_style = styles[0]

        # Check the worldview property
        assert isinstance(first_style.worldview, BasemapStylesWorldview)
        # Set the worldview to 'united_states'
        first_style.worldview = BasemapStylesWorldview.UNITED_STATES
        assert first_style.worldview == BasemapStylesWorldview.UNITED_STATES

    def test_basemap_styles_service_get(self):
        """
        Test getting a specific basemap style by its ID.
        """
        basemap_styles_service = self.wm.basemap.basemap_styles_service
        styles = basemap_styles_service.styles
        first_style = styles[0]

        # Get the style by ID
        style_by_name = basemap_styles_service.get_style(
            basemap_styles_service.styles_names[0],
            language=BasemapStylesLanguage.ENGLISH,
            place=BasemapStylesPlace.ALL,
            worldview=BasemapStylesWorldview.UNITED_STATES,
        )
        assert isinstance(style_by_name, BasemapStyle)
        assert style_by_name.name == first_style.name
        assert style_by_name.language == BasemapStylesLanguage.ENGLISH
        assert style_by_name.worldview == BasemapStylesWorldview.UNITED_STATES
        assert style_by_name.place == BasemapStylesPlace.ALL

    def test_setting_basemap_styles_service(self):
        """
        Test setting a basemap style service to the map.
        """
        basemap_styles_service = self.wm.basemap.basemap_styles_service
        styles = basemap_styles_service.styles
        first_style = styles[0]

        self.wm.basemap.basemap = first_style
        assert isinstance(self.wm.basemap.basemap, dict)


if __name__ == "__main__":
    unittest.main()
