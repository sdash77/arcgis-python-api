from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import unittest
import os
import time
import sys
import logging
log = logging.getLogger()

from automation._classes.TestNotebook.JupyterClassicNotebookServer \
    import JupyterClassicNotebookServer

NB_CELL_POLLING_INTERVAL_SEC = 2
PRE_WIDGET_SCREENSHOT_SLEEP_SEC = 10
DEFAULT_IMPLICIT_WAIT_SEC = 10
INBETWEEN_WIDGET_SCREENSHOT_SLEEP_SEC = 5
AFTER_SAVE_SLEEP_SEC = 10

class NotebookRunnerSelenium:
    def __init__(self, notebook_file_path, notebook_timeout, output_dir,
                 active_jupyter_backend = None, browser = "Chrome"):
        self.notebook_file_path = notebook_file_path
        self.notebook_timeout = notebook_timeout
        self.active_jupyter_backend = active_jupyter_backend
        self.output_dir = output_dir
        if "chrome" in browser.lower():
            self.driver = webdriver.Chrome()
        elif "firefox" in browser.lower():
            self.driver = webdriver.Firefox()
        else:
            raise Exception("Could not infer browser to run notebook on")

    def run_notebook(self):
        try:
            if self.active_jupyter_backend:
                self._run_notebook()
            else:
                with JupyterClassicNotebookServer() as j:
                    self.active_jupyter_backend = j
                    self._run_notebook()
                    self.active_jupyter_backend = None
        except:
            # Yes, even catch keyboard interrupts
            if self.active_jupyter_backend:
                self.active_jupyter_backend.__exit__()
            raise

    def _run_notebook(self):
        self._initialize_notebook()
        self._run_each_cell_until_bottom()
        self._take_screenshots_of_any_map_widgets()
        self._save_notebook()

    def _initialize_notebook(self):
        self.driver.implicitly_wait(self.notebook_timeout)
        nb_url = self.active_jupyter_backend.base_url + "notebook.ipynb"
        self.driver.get(nb_url)
        self._initial_num_code_cells = self._get_num_code_cells()
        self._initialize_run_button_element()
        self._initialize_save_button_element()
 
    def _initialize_run_button_element(self):
        self._run_button = self.driver.find_element_by_xpath(
            '//button[@title="Run"]')

    def _initialize_save_button_element(self):
        self._save_button = self.driver.find_element_by_xpath(
            '//button/[@title="Save and Checkpoint"]')

    def _save_notebook(self):
        self._save_button.click()
        time.sleep(AFTER_SAVE_SLEEP_SEC)

    def _take_screenshots_of_any_map_widgets(self):
        time.sleep(PRE_WIDGET_SCREENSHOT_SLEEP_SEC)
        map_widget_divs = self.driver.find_elements_by_class_name(
            "arcgisMapIPyWidgetDiv")
        for widget_div in map_widget_divs:
            widget_div.click()
            self.driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT_SEC)
            for input_div in widget_div.find_elements_by_tag_name("input"):
                input_div.send_keys(Keys.CONTROL, Keys.SHIFT, "P")
                self.driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT_SEC)
            time.sleep(INBETWEEN_WIDGET_SCREENSHOT_SLEEP_SEC)

    def _run_each_cell_until_bottom(self):
        seconds_running = 0
        while True:
            time.sleep(NB_CELL_POLLING_INTERVAL_SEC)
            seconds_cell_running += NB_CELL_POLLING_INTERVAL_SEC
            if self._any_cell_currently_running():
                continue
            elif self._bottom_of_notebook_reached():
                break
            elif seconds_cell_running > self.notebook_timeout:
                raise Exception("Cell has timed out, failing...")
            else:
                seconds_cell_running = 0
                self._run_button.click()

    def _any_cell_currently_running(self):
        cell_prompt_input_elements = self.driver.find_elements_by_class_name("input_prompt")
        def is_running(cell_prompt_input_el):
            return "*" in cell_prompt_input_el.text
        return any(el for el in cell_prompt_input_elements if is_running(el))

    def _get_num_code_cells(self):
        return len(self.driver.find_elements_by_class_name("code_cell"))

    def _bottom_of_notebook_reached(self):
        return self._get_num_code_cells() != self._initial_num_code_cells

    def _save_notebook(self):
        self._save_button.click()
        time.sleep(AFTER_SAVE_SLEEP_SEC)

