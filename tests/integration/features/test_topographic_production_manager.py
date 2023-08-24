import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.features._topographic import TopographicProductionManager
from arcgis.gis.server.catalog import ServicesDirectory

sd = ServicesDirectory(
    url="https://rextapilnxsvr01.esri.com/server",
    username="siteadmin",
    password="esri.agp2",
    verify_cert=False,
)

# If data missing in server: \\qalab_server\pydata\v109\geosaurus\topographic_data
# Go to folder and use server manager to publish the SD file
# Create Topographic Service
topo = TopographicProductionManager(
    "https://rextapilnxsvr01.esri.com/server/rest/services/TMServer_Fortlewis/TopographicProductionServer",
    sd,
)


class TestTopographicProductionManager(unittest.TestCase):
    """Tests the Topographic Production Service"""

    def test_get_products(self):
        products = topo.products()
        assert products

    def test_get_product(self):
        product = topo.product("ExampleProduct")
        assert product
        assert product["name"] == "ExampleProduct"

    def test_add_product(self):
        """Test the add_product method"""
        # Get all the products
        products = topo.products(include_def=True)
        number_products = len(products["products"])
        # Grab the definition of the first one and change it's name
        product = products["products"][0]["productDefinition"]
        product["name"] = "Python API Test"
        new_product = topo.add_product(product)

        assert new_product["success"] == True
        assert new_product["productName"] == "Python API Test"

        # Get all the products again to compare
        products_updated = topo.products()
        assert len(products_updated["products"]) == number_products + 1

    def test_remove_product(self):
        """Test remove product"""
        # Get all the products
        products = topo.products(include_def=True)
        number_products = len(products["products"])
        # Remove the product added in the add_product test
        removed_product = topo.remove_product("Python API Test")
        assert removed_product["success"] == True
        assert removed_product["productName"] == "Python API Test"

        # Get all the products again to compare
        products_updated = topo.products()
        assert len(products_updated["products"]) == number_products - 1

    def test_generate_product(self):
        """Test generate product"""
        # Get all the products
        products = topo.products(include_def=True)
        product = products["products"][0]
        generated = topo.generate_product(
            product["name"],
            "TRD_4_5",
            "https://rextapilnxsvr01.esri.com/server/rest/services/TMServer_Fortlewis/MapServer/0",
            "234",
            "aprx",
        )

        assert generated["jobId"]
        assert generated["statusUrl"]
        assert generated["success"] == True


if __name__ == "__main__":
    unittest.main()
