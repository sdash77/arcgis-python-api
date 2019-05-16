from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import unittest
import os
import time
import sys
import logging
log = logging.getLogger()

from automation._classes.JupyterClassicNotebookServer import JupyterClassicNotebookServer

class TestNotebookSelenium(unittest.TestCase):
    def __init__(self, notebook_file_path, output_dir, notebook_timeout, 
                 jenkins_job_url=None, active_jupyter_backend = None,
                 browser = "Chrome"):
        self._notebook_file_path = notebook_file_path
        self.output_dir = output_dir
        self.notebook_timeout = notebook_timeout
        self.jenkins_job_url = jenkins_job_url
        self.active_jupyter_backend = active_jupyter_backend
        if "chrome" in browser.lower():
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Firefox()

    def runTest(self):
        if self.active_jupyter_backend:
            self._runTest()
        else:
            with JupyterClassicNotebookServer() as j:
                self.active_jupyter_backend = j
                self._runTest();
                self.active_jupyter_backend = None

    def _runTest(self):
        self.driver.implicitly_wait(10)
        nb_url = self.active_jupyter_backend.base_url + "notebook.ipynb"
        self.driver.get(nb_url)
        run_toolbar = self.driver.find_element_by_id("run_int")
        run_button = self.driver.find_element_by_xpath('//button[@title="Run"]')
        import time
        for i in range(0,5):
            time.sleep(1)
            run_button.click()
