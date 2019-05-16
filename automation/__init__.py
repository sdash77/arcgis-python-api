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

from automation.automation_cleanup import automation_cleanup
from automation.automation_setup import automation_setup
from automation.build_conda_package import build_conda_package
from automation.build_dev_website_and_publish import build_dev_website_and_publish
from automation.build_documentation import build_documentation
from automation.build_pip_package import build_pip_package
from automation.publish_to_ftp_site import publish_to_ftp_site
from automation.run_dev_website_tests import run_dev_website_tests
from automation.run_integration_tests import run_integration_tests
from automation.run_notebook_tests import run_notebook_tests
from automation.stage_notebooks_for_dev_web_repo import stage_notebooks_for_dev_web_repo
from automation.build_dummy_dev_site import build_dummy_dev_site
