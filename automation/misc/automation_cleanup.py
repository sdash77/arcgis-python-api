import os
import logging
log = logging.getLogger()

from automation._common import * 

def automation_cleanup(*args, **kwargs):
    log.info("Automated process is about to exit.")
    log.info("To view log file containing all INFO and DEBUG messages, go to "\
             "{}".format(os.path.join(STAGING_DIR, "log.log")))
    log.info("Note: if you're viewing this in Jenkins, Console Output (DEBUG)"\
             " link on the finished job should contain all the DEBUG messages"\
             ". (Console Output link just contains the INFO messages)")
