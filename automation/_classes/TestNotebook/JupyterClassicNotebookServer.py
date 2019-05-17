import os
import tempfile
import time
import socket
from subprocess import Popen, PIPE, STDOUT
import logging
log = logging.getLogger()

from automation._common import run_shell_command

class JupyterClassicNotebookServer:
    def __init__(self, notebook_root_dir, port=8888):
        self.port = port
        self.notebook_root_dir = notebook_root_dir
        try:
            if os.name == "posix":
                shell_cmd = "which jupyter"
            elif os.name == "nt":
                shell_cmd = "where jupyter"
            self._jupyter_exe_loc = run_shell_command(shell_cmd).split("\n")[0]
            self._config_file_path = os.path.join(tempfile.gettempdir(),
                                                  "config.py")
            with open(self._config_file_path, "w+") as f:
                f.write('c.NotebookApp.token = "" # disables auth')
        except Exception as e:
            raise Exception("Couldn't determine Jupyter executable location")

    def _port_in_use(self, port_num):
        output = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1',port_num))
        if result == 0:
           output = False
        else:
           output = True
        sock.close()
        return output

    def __enter__(self):
        args = [self._jupyter_exe_loc, "notebook", 
                              f"--config={self._config_file_path}",
                              f"--no-browser",
                              f"--port={self.port}"]
        log.debug(f"calling Popen({args})")
        self.process = Popen(args, cwd=self.notebook_root_dir, 
                             stdout=PIPE, stderr=STDOUT)
        self.base_url = f"http://127.0.0.1:{self.port}/notebooks/"
        time.sleep(10) # Just incase
        return self

    def __exit__(self, type, value, traceback):
        log.info("Shutting down Jupyter Server instance...")
        self.process.terminate()
