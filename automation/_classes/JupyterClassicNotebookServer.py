import os
import tempfile
import time
from subprocess import Popen, PIPE, STDOUT
import logging
log = logging.getLogger()

from automation._common import run_shell_command

class JupyterClassicNotebookServer:
    def __init__(self, port=8888):
        self.port = port
        try:
            if os.name == "posix":
                shell_cmd = "which jupyter"
            elif os.name == "nt":
                shell_cmd = "where jupyter"
            self._jupyter_exe_loc = run_shell_command(shell_cmd).split("\n")[0]
            config_file_path = os.path.join(tempfile.gettempdir(), "config.py")
            with open(config_file_path, "w+") as f:
                f.write('c.NotebookApp.token = "" # disables auth')
                self._config_file_path = f.name
        except Exception as e:
            raise Exception("Couldn't determine Jupyter executable location")

    def __enter__(self):
        args = [self._jupyter_exe_loc, "notebook", 
                              f"--config={self._config_file_path}",
                              f"--no-browser",
                              f"--port={self.port}"]
        log.debug(f"calling Popen({args}")
        self.process = Popen(args, stdout=PIPE, stderr=STDOUT)
        self.base_url = f"http://localhost:{self.port}/notebooks/"
        time.sleep(10) # Just incase
        return self

    def __exit__(self, type, value, traceback):
        log.info("Shutting down Jupyter Server instance...")
        self.process.terminate()
