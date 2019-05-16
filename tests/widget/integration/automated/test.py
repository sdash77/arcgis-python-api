from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import subprocess
import unittest
import os
import subprocess
from subprocess import Popen
import tempfile
import time

def run_shell_command(cmd, throw_exc_on_fail=True):
    try:
        byte_output = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        str_output = byte_output.decode("utf-8")
        return str_output
    except subprocess.CalledProcessError as e:
        log.warn("cmd failed, returned non-zero code. Output:\n"\
                 "{}".format(e.output.decode("utf-8")))
        if throw_exc_on_fail:
            raise e

class SeleniumNotebookTest(unittest.TestCase):
    def __init__(self, notebook_file_path, output_dir, notebook_timeout, jenkins_job_url=None):
        self._notebook_file_path = notebook_file_path
        self.output_dir = output_dir
        self.notebook_timeout = notebook_timeout
        self.jenkins_job_url = jenkins_job_url

    def runTest(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://localhost:8888/?token=cab8d092640597c1cdf34cfd585911f8af69ad20c2c56293")
        self.driver.get("http://localhost:8888/notebooks/Untitled357.ipynb?kernel_name=python3")
        self.driver.implicitly_wait(10)
        run_toolbar = self.driver.find_element_by_id("run_int")
        run_button = self.driver.find_element_by_xpath('//button[@title="Run"]')
        import time
        for i in range(0,5):
            time.sleep(1)
            run_button.click()

class JupyterNotebookServerInst:
    def __init__(self):
        try:
            if os.name == "posix":
                shell_cmd = "which jupyter"
            elif os.name == "nt":
                shell_cmd = "where jupyter"
            self._jupyter_exe_loc = run_shell_command(shell_cmd).split("\n")[0]
            with open("./config.py") as f:
                f.write('c.NotebookApp.token = "" # disables auth')
                self._config_file_path = f.name
        except Exception as e:
            raise Exception("Couldn't determine Jupyter executable location")
    

    def __enter__(self):
        args = [self._jupyter_exe_loc, "notebook", 
                              f"--config={self._config_file_path}"]
        print(f"calling Popen({args}")
        self.process = Popen(args)
        time.sleep(10) # Just incase
        return self

    def __exit__(self, type, value, traceback):
        self.process.terminate()

if __name__ == "__main__":
    with JupyterNotebookServerInst() as j:
        print("I have j")
    #t = SeleniumNotebookTest("","","")
    #t.runTest()
