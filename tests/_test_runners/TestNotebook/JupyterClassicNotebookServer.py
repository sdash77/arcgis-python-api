import os
import tempfile
import time
import socket
from subprocess import Popen, PIPE, STDOUT
import logging
log = logging.getLogger()

from utils._common import *

MAX_NUM_PORTS_TO_TRY = 5

class JupyterClassicNotebookServer:
    def __init__(self, notebook_root_dir, port=8888):
        self.port = port
        self.notebook_root_dir = notebook_root_dir
        try:
            self._config_file_path = os.path.join(tempfile.gettempdir(),
                                                  "config.py")
            with open(self._config_file_path, "w+") as f:
                f.write(f'c.NotebookApp.token = "" # disables auth\n')
        except Exception as e:
            raise Exception("Couldn't determine Jupyter executable location")

    def _port_in_use(self, port_num):
        output = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1',port_num))
        if result == 0:
           output = True
        else:
           output = False
        sock.close()
        return output

    def _resolve_port(self):
        """Test ports until you find an open one, set to self.port"""
        ports_tested = []
        for port in range(self.port, self.port + MAX_NUM_PORTS_TO_TRY):
            ports_tested.append(port)
            if not self._port_in_use(port):
                self.port = port
                return
        raise Exception(f"Ports {ports_tested} are ALL in use by other " + \
                        f"processes, will not start Jupyter server. Check " + \
                        f"that you're properly shutting down jupyter servers.")

    def __enter__(self):
        self._resolve_port()
        cmd = f"python -m jupyter notebook "\
              f"--config={self._config_file_path} "\
              f"--no-browser "\
              f"--port={self.port} "
        log.debug(f"calling Popen({cmd})")
        self.process = Popen(cmd, cwd=self.notebook_root_dir,shell=True) 
        #                     stdout=PIPE, stderr=STDOUT, shell=True)
        self.base_url = f"http://localhost:{self.port}/notebooks/"
        time.sleep(10) # Just incase
        return self

    def __exit__(self, type, value, traceback):
        log.info("Shutting down Jupyter Server instance...")
        self.process.terminate()
        self._try_kill_process_on_port()

    def _try_kill_process_on_port(self):
        log.info(f"Attempting to kill process running on port {self.port}")
        try:
            if os.name == "posix":
                run_shell_command(f"kill $(lsof -i:{self.port})")
            elif os.name == "nt":
                out = run_shell_command(f"netstat -ano | findstr :{self.port}")
                pid = out.split("\n")[0].lower().split("listening")[1].strip()
                run_shell_command(f"taskkill /pid {pid} /f")
        except Exception as e:
            log.warn(f"Could not kill jupyter process running on {self.port}."\
                     f" Beware of a leak of unkilled server instances...")
