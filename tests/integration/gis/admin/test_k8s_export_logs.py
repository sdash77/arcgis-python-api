import os
import unittest
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_k8s
@integration_test
class TestKubernetesExportLogs(unittest.TestCase):
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
