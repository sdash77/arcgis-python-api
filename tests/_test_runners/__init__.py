import logging
log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)
formatter_str = \
    u'-----    %(levelname)s    |    '\
     '%(asctime)s    |    '\
     '%(filename)s line %(lineno)d'\
     '     -----\n'\
     '"%(message)s"'
formatter = logging.Formatter(formatter_str)

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)

from _test_runners.read_suite_file import read_suite_file
from _test_runners.run_suite import run_suite
