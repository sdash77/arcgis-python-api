import sys

import unittest
from arcgis.auth import EsriSession
from arcgis.auth.tools import no_ssl_verification


from contextlib import contextmanager
import warnings


class WarnAssertionsMixin:
    @contextmanager
    def assertNoWarnings(self):
        try:
            warnings.simplefilter("error")
            yield
        finally:
            warnings.resetwarnings()

    @contextmanager
    def assertWarnings(self, messages):
        """
        Asserts that the given messages are issued in the given order.
        """
        if not messages:
            raise RuntimeError("Use assertNoWarnings instead!")

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            for mod in sys.modules.values():
                if hasattr(mod, "__warningregistry__"):
                    mod.__warningregistry__.clear()
            yield
            warning_list = [w.message.args[0] for w in warning_list]
            self.assertEquals(messages, warning_list)


class TestNoSSLContext(unittest.TestCase, WarnAssertionsMixin):
    """
    Tests the no_ssl_verification
    """

    def test_no_ssl_verification(self):
        """
        tests the contextmanager
        """

        with self.assertNoWarnings() as cm:
            with no_ssl_verification():
                with EsriSession() as session:
                    resp = session.get(
                        "https://www.arcgis.com/sharing/rest?f=json"
                    )


if __name__ == "__main__":
    unittest.main()
