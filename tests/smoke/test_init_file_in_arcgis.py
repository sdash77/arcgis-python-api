import os, re
import unittest
from glob import glob
from utils.imports import *


class TestInitFileInArcgis(unittest.TestCase):

    def test_init_in_arcgis_module(self):
        clear_arcgis_import_cache()
        import arcgis

        arcgis_dir = os.path.dirname(arcgis.__file__)
        pattern = os.path.join(arcgis_dir, "**", "*.py")
        all_py_dirs = set([os.path.dirname(x) for x in glob(pattern, recursive=True)])
        actual = [
            x for x in all_py_dirs if not os.path.exists(os.path.join(x, "__init__.py"))
        ]
        expected = 0
        init_not_found_list = []
        exception_list = ["mmseg_config", "mmdetection_config"]
        for path in actual:
            exception_found = False
            for exceptions in exception_list:
                if exceptions in path:
                    exception_found = True
                    break
            if not exception_found:
                init_not_found_list.append(path[len(arcgis_dir) :])
        assert len(init_not_found_list) == expected, "__init__.py file not found in " + str(
            init_not_found_list
        )
        clear_arcgis_import_cache()


if __name__ == "__main__":

    unittest.main()
