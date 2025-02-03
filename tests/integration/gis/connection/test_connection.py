import sys

sys.path.insert(0, r"C:\SVN\geosaurus_issue_12358\src")
sys.path.insert(1, r"C:\SVN\geosaurus_issue_12358\tests")


#######################################################################
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

from arcgis.gis._impl._con import Connection

enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestConnectionClass(unittest.TestCase):
    def test_connection(self):
        c = Connection(session=self.gis.session)
        assert c._session == self.gis.session


if __name__ == "__main__":
    unittest.main()
