import sys
import os
# REMOVE ME
sys.path.insert(0, os.path.join("/Users/davi9349/devel/geofork/"))
#REMOVE ME
from automation._classes import *

if __name__ == "__main__":
    t = TestNotebookSelenium(notebook_file_path="", output_dir="", 
                             notebook_timeout="",
                             jenkins_job_url=None, 
                             active_jupyter_backend = None,
                             browser = "Chrome")
    t.runTest()
