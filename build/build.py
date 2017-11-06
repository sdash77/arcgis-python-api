import os
import sys
import subprocess
import logging
log = logging.getLogger()

from __init__ import *

def build(args):
    

if __name__ == "__main__":
    try:
        build(sys.argv)
    except Exception as e:
        log.info("Unhandled exception caught: Adding to log...")
        log.exception(e)
        log.info("Succesfully logged exception: Raising it again...") 
        raise e
