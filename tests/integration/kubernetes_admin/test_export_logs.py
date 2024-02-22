import sys
import os
import unittest
from utils.decorators import profiles, default_timeout
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.k8s
class TestKubernetesExportLogs(unittest.TestCase):
    @default_timeout
    def test_export_log(self):
        admin = self.gis.admin
        lm = admin.logs
        res = lm.export()
        assert isinstance(res, str)
        assert os.path.isfile(res)
        try:
            os.remove(res)
        except:
            pass

    @default_timeout
    def test_export_log_parameters(self):
        admin = self.gis.admin
        lm = admin.logs
        res = lm.export(
            query="error",
            start_time=None,
            end_time=None,
            level="VERBOSE",
            log_code=None,
            users=None,
            request_ids=None,
            service_types=None,
            source=None,
            stack_traces=True,
            out_folder=None,
        )
        assert isinstance(res, str)
        assert os.path.isfile(res)
        try:
            os.remove(res)
        except:
            pass


if __name__ == "__main__":
    unittest.main()
