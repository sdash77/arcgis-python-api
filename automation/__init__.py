import logging
log = logging.getLogger()

from automation._common import *

log.setLevel(logging.DEBUG)
log_file_path = os.path.join(STAGING_DIR, "log.log")
formatter_str = \
    u'-----    %(levelname)s    |    '\
     '%(asctime)s    |    '\
     '%(filename)s line %(lineno)d'\
     '     -----\n'\
     '"%(message)s"'
formatter = logging.Formatter(formatter_str)

file_handler = logging.FileHandler(log_file_path, "w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)

from automation.misc.automation_cleanup import automation_cleanup
from automation.misc.automation_setup import automation_setup

from automation.package_building.build_conda_package import build_conda_package
from automation.package_building.build_pip_package import build_pip_package
from automation.package_building.publish_to_ftp_site import publish_to_ftp_site

from automation.documentation.build_documentation import build_documentation

from automation.dev_site.stage_notebooks_for_dev_web_repo import stage_notebooks_for_dev_web_repo
from automation.dev_site.build_dummy_dev_site import build_dummy_dev_site

from automation.testing_utils.run_test_suite import run_test_suite
