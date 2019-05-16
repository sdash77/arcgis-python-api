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

POLLING_INTERVAL_SEC = 2

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
        self.driver.implicitly_wait(self.notebook_timeout)
        nb_url = self.active_jupyter_backend.base_url + "notebook.ipynb"
        self.driver.get(nb_url)
        self._initial_num_code_cells = self._get_num_code_cells()
        run_toolbar = self.driver.find_element_by_id("run_int")
        run_button = self.driver.find_element_by_xpath('//button[@title="Run"]')
        self._run_notebook(run_button)

    def _run_notebook(self, run_button):
        while True:
            time.sleep(POLLING_INTERVAL_SEC)
            if self._any_cell_currently_running():
                print("Someone still running, waiting...")
                continue
            elif self._bottom_of_notebook_reached():
                break
            else:
                run_button.click()
        log.info("Notebook finished running, exiting...")

    def _any_cell_currently_running(self):
        cell_prompt_input_elements = self.driver.find_elements_by_class_name("input_prompt")
        def is_running(cell_prompt_input_el):
            return "*" in cell_prompt_input_el.text
        return any(el for el in cell_prompt_input_elements if is_running(el))

    def _get_num_code_cells(self):
        return len(self.driver.find_elements_by_class_name("code_cell"))

    def _bottom_of_notebook_reached(self):
        return self._get_num_code_cells() != self._initial_num_code_cells
