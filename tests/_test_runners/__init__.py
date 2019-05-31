import logging
# TODO: find more elgant logging solution
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

from _test_runners.read_suite import read_suite
from _test_runners.run_suite import run_suite
from _test_runners._common import *
