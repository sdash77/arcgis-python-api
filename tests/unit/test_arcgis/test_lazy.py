import unittest
from arcgis.auth.tools import LazyLoader


class TestLazyLoader(unittest.TestCase):
    """tests the lazy loading class"""

    def test_lazy_import(self):
        json = LazyLoader("json")
        assert json

    def test_lazy_import_strict(self):
        json = LazyLoader("json", strict=True)
        assert json

    def test_lazy_import_strict_failure(self):
        with self.assertRaises(ModuleNotFoundError) as context:
            LazyLoader("fake234qagadfg43t243sdfg", strict=True)

    def test_exists_method(self):
        assert LazyLoader.check_module_exists("json") == True
        assert (
            LazyLoader.check_module_exists("the_amazing_chester_the_dog")
            == False
        )

    def test_lazy_import_submodule(self):
        cf = LazyLoader("concurrent", "futures")
        assert cf.ThreadPoolExecutor


if __name__ == "__main__":
    unittest.main()
