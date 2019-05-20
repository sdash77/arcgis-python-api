import os
import time
import sys
import shutil
import tempfile
import logging
log = logging.getLogger()

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat

from automation._classes.TestNotebook.JupyterClassicNotebookServer \
    import JupyterClassicNotebookServer

from automation._classes.TestNotebook.NotebookRunnerResult \
    import NotebookRunnerResult

NB_CELL_POLLING_INTERVAL_SEC = 2
PRE_WIDGET_SCREENSHOT_SLEEP_SEC = 10
DEFAULT_IMPLICIT_WAIT_SEC = 10
INBETWEEN_WIDGET_SCREENSHOT_SLEEP_SEC = 5
AFTER_SAVE_SLEEP_SEC = 10
GENERIC_SLEEP_SEC = 5

class NotebookRunnerSelenium:
    def __init__(self, notebook_file_path, output_dir, cell_timeout_sec = 300,
                 active_jupyter_backend = None, browser = "Chrome"):
        self.notebook_file_path = notebook_file_path
        self.cell_timeout_sec = cell_timeout_sec
        self.active_jupyter_backend = active_jupyter_backend
        self.output_dir = output_dir
        self.browser = browser

        self.notebook_file_name_no_ext = os.path.splitext(os.path.basename(
            self.notebook_file_path))[0]

    def _initialize_driver(self):
        if "chrome" in self.browser.lower():
            self.driver = webdriver.Chrome()
        elif "firefox" in self.browser.lower():
            self.driver = webdriver.Firefox()
        else:
            raise Exception("Could not infer browser to run notebook on")
        self.driver.fullscreen_window()

    def _deinitialize_driver(self):
        self.driver.close()

    def run_notebook(self):
        self._initialize_driver()
        output = None
        try:
            if self.active_jupyter_backend:
                output = self._run_notebook()
            else:
                tmp_dir = tempfile.mkdtemp()
                with JupyterClassicNotebookServer(tmp_dir) as j:
                    self.active_jupyter_backend = j
                    output = self._run_notebook()
                    self.active_jupyter_backend = None
                shutil.rmtree(tmp_dir)
        except:
            # Yes, even catch keyboard interrupts
            if self.active_jupyter_backend:
                # Triple check that we've closed all jupyter server insts
                self.active_jupyter_backend.__exit__(None, None, None)
            raise
        self._deinitialize_driver()
        return output

    def _run_notebook(self):
        # Stage the notebook in a location Jupyter Server can open it
        shutil.copy(self.notebook_file_path,
                    self.active_jupyter_backend.notebook_root_dir)
        
        # Run the notebook, take screenshots of widgets, save it
        self._initialize_selenium()
        self._run_each_cell_until_bottom()
        self._take_screenshots_of_any_map_widgets()
        self._save_notebook()

        # Convert to HTML, then copy both HTML and executed nb to output_dir
        executed_notebook_path = os.path.join(
            self.active_jupyter_backend.notebook_root_dir,
            self.notebook_file_name_no_ext + ".ipynb")
        shutil.copy(executed_notebook_path, self.output_dir)
        output_ipynb_path = os.path.join(self.output_dir,
            self.notebook_file_name_no_ext + ".ipynb")
        output_html_path = os.path.join(self.output_dir,
            self.notebook_file_name_no_ext + ".html")
        self._convert_ipynb_to_html(output_ipynb_path, output_html_path)

        return NotebookRunnerResult(output_ipynb_path = output_ipynb_path,
                                    output_html_path = output_html_path)

    def _initialize_selenium(self):
        self.driver.implicitly_wait(GENERIC_SLEEP_SEC)
        nb_url = self.active_jupyter_backend.base_url + \
                f"{self.notebook_file_name_no_ext}.ipynb"
        self.driver.get(nb_url)
        time.sleep(GENERIC_SLEEP_SEC)
        self._initial_num_code_cells = self._get_num_code_cells()
        self._initialize_run_button_element()
        self._initialize_save_button_element()
 
    def _initialize_run_button_element(self):
        self._run_button = self.driver.find_element_by_xpath(
            '//button[@title="Run"]')

    def _initialize_save_button_element(self):
        self._save_button = self.driver.find_element_by_xpath(
            '//button[@title="Save and Checkpoint"]')

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
        seconds_cell_running = 0
        while True:
            time.sleep(NB_CELL_POLLING_INTERVAL_SEC)
            seconds_cell_running += NB_CELL_POLLING_INTERVAL_SEC
            if self._any_cell_currently_running():
                continue
            elif self._bottom_of_notebook_reached():
                break
            elif seconds_cell_running > self.cell_timeout_sec:
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

    def _convert_ipynb_to_html(self, ipynb_path, html_path):
        with open(ipynb_path, "r",
                  encoding="utf-8") as input_nb_file:
            #Execute input notebook
            input_nb = nbformat.read(input_nb_file,
                as_version = nbformat.current_nbformat)
            html_exporter = HTMLExporter()
            (body, resources) = html_exporter.from_notebook_node(input_nb)
            with open(html_path, "w",
                      encoding="utf-8") as output_html:
                output_html.write(body)
