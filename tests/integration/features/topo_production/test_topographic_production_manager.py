import unittest
from arcgis.features._topographic import TopographicProductionManager
from utils.decorators import integration_test, profiles
from utils.data_utils import get_feature_layer_url, ServerTypeEnum


@profiles.enterprise
@integration_test
class TestTopographicProductionManager(unittest.TestCase):
    """Tests the Topographic Production Service"""

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        # If data missing in server: \\qalab_server\pydata\v109\geosaurus\topographic_data
        # Go to folder and use server manager to publish the SD file

        # Create Topographic Service
        topo_url = get_feature_layer_url(
            cls.gis, "TMServer_Fortlewis", ServerTypeEnum.TOPOGRAPHIC
        )
        topo = TopographicProductionManager(
            topo_url,
            cls.gis,
        )
        if len(topo.products()["products"]) == 0:
            # Add a prodcut if none exists already
            product_def = {
                "version": 0,
                "name": "ExampleProduct",
                "type": "MTM",
                "gridType": "TM50",
                "description": "Test Masking Product",
                "sheetIDField": "NRN",
                "productVersions": [
                    {"name": "TRD_4_5", "template": "MTM50_Layout.pagx"}
                ],
                "resources": [
                    {"name": "SourceWorkspace", "type": 3, "value": ""},
                    {"name": "AOILayer", "type": 2, "value": ""},
                    {"name": "SheetID", "type": 1, "value": ""},
                    {"name": "Layout", "type": 6, "value": ""},
                    {"name": "ProductFiles", "type": 7, "value": ""},
                ],
                "operations": [
                    {
                        "name": "MapResource",
                        "type": 11,
                        "description": "Update BaseMap DataSources",
                        "parameters": [{"name": "in_map", "value": "BaseMap"}],
                    },
                    {
                        "name": "Grid",
                        "type": 4,
                        "description": "BaseMap Grid",
                        "toolName": "MakeGridsAndGraticulesLayer_topographic",
                        "validation": 2,
                        "properties": {
                            "type": "PropertySet",
                            "propertySetItems": ["AddOutputToMap", "BaseMap"],
                        },
                        "parameters": [
                            {"name": "in_grid_xml", "value": "[GridLocator]\\BaseMap"},
                            {"name": "area_of_interest", "value": "[AOILayer]"},
                            {
                                "name": "target_feature_dataset",
                                "value": "[SourceWorkspace]\\BM_GRD",
                            },
                            {"name": "out_layer_name", "value": "BMGrid"},
                            {"name": "grid_name", "value": "BMGrid"},
                            {"name": "configure_layout", "value": "CONFIGURE_LAYOUT"},
                            {"name": "layout", "value": "[Layout]"},
                            {"name": "map_frame", "value": "BaseMap Map Frame"},
                        ],
                    },
                    {
                        "name": "CreateMasks",
                        "type": 7,
                        "description": "Create Masks for Base Map",
                        "toolName": "MakeMasksFromRules_topographic",
                        "validation": 2,
                        "properties": {
                            "type": "PropertySet",
                            "propertySetItems": ["MapName", "BaseMap"],
                        },
                        "parameters": [
                            {"name": "in_map", "value": "BaseMap"},
                            {
                                "name": "rule_file",
                                "value": "[ProductFiles]\\MTM_Basemap_Masking_Rules.xml",
                            },
                            {
                                "name": "out_feature_dataset",
                                "value": "[SourceWorkspace]\\Masks",
                            },
                        ],
                    },
                    {
                        "name": "ApplyMasks",
                        "type": 7,
                        "description": "Apply Masks for Base Map",
                        "toolName": "ApplyMasksFromRules_topographic",
                        "validation": 2,
                        "properties": {
                            "type": "PropertySet",
                            "propertySetItems": ["MapName", "BaseMap"],
                        },
                        "parameters": [
                            {"name": "in_map", "value": "BaseMap"},
                            {
                                "name": "rule_file",
                                "value": "[ProductFiles]\\MTM_Basemap_Masking_Rules.xml",
                            },
                            {
                                "name": "in_feature_dataset",
                                "value": "[SourceWorkspace]\\Masks",
                            },
                        ],
                    },
                ],
            }
            topo.add_product(product_def)
        cls.topo = topo

    def test_get_products(self):
        products = self.topo.products()
        assert products

    def test_get_product(self):
        product = self.topo.product("ExampleProduct")
        assert product
        assert product["name"] == "ExampleProduct"

    def test_add_product(self):
        """Test the add_product method"""
        # Get all the products
        products = self.topo.products(include_def=True)
        number_products = len(products["products"])
        # Grab the definition of the first one and change it's name
        product = products["products"][0]["productDefinition"]
        product["name"] = "Python API Test"
        new_product = self.topo.add_product(product)

        assert new_product["success"]
        assert new_product["productName"] == "Python API Test"

        # Get all the products again to compare
        products_updated = self.topo.products()
        assert len(products_updated["products"]) == number_products + 1

    def test_remove_product(self):
        """Test remove product"""
        # Get all the products
        products = self.topo.products(include_def=True)
        number_products = len(products["products"])
        # Remove the product added in the add_product test
        removed_product = self.topo.remove_product("Python API Test")
        assert removed_product["success"]
        assert removed_product["productName"] == "Python API Test"

        # Get all the products again to compare
        products_updated = self.topo.products()
        assert len(products_updated["products"]) == number_products - 1

    def test_generate_product(self):
        """Test generate product"""
        # Get all the products
        map_server_url = get_feature_layer_url(
            self.gis, "TMServer_Fortlewis", ServerTypeEnum.MAP_SERVER, layer_id=39
        )
        products = self.topo.products(include_def=True)
        product = products["products"][0]
        generated = self.topo.generate_product(
            name=product["name"],
            version="TRD_4_5",
            area_interest_layer=map_server_url,
            area_interest_feature_id="72",
            output_type={
                "outputType": "APRX",
                "outputFiles": ["Geodatabase", "Project"],
            },
        )

        assert generated["jobId"]
        assert generated["statusUrl"]
        assert generated["success"]


if __name__ == "__main__":
    unittest.main()
