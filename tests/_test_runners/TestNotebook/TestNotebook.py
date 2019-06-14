import sys
import os
import unittest
import logging
log = logging.getLogger()

from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat

from _test_runners.TestNotebook.NotebookRunnerNbConvert \
    import NotebookRunnerNbConvert
from _test_runners.TestNotebook.NotebookRunnerSelenium \
    import NotebookRunnerSelenium

class TestNotebook(unittest.TestCase):
    """Given a notebook file, run it and output the ran notebook as HTML.
    Check the notebook for any errors in the python code's execution
    (unhandled exceptions, if output_type == "error"), fail the test if so.
    """
    def __init__(self, notebook_file_path, output_dir, cell_timeout_sec = 300,
                 jenkins_job_url=None, 
                 notebook_runner="nbconvert",
                 active_jupyter_backend = None, # only used with selenium
                 browser = None, # only used with selenium
                 **kwargs):
        """notebook_file_path is the path to the notebook to test
        output_dir is where all ran notebooks and converted html go to
        notebook_timeout is the max number of seconds a CELL in a nb can run
        jenkins_job_url is optional, it is used to print out a link to the
        outputted notebook if the test notebook suite is running on Jenkins
        nb_runner is a string that specifies whether to run the notebook
        using the standard nbconvert (no widget output) or using selenium
        (widget output and live javascript running in a physical browser)
        """
        self.notebook_file_path = notebook_file_path
        self.output_dir = output_dir
        self.jenkins_job_url = jenkins_job_url
        self.notebook_file_name_no_ext = os.path.splitext(os.path.basename(
            notebook_file_path))[0]

        # Set up notebook runner
        nb_runner_kwargs = {}
        nb_runner_kwargs["notebook_file_path"] = notebook_file_path
        nb_runner_kwargs["output_dir"] = output_dir
        nb_runner_kwargs["cell_timeout_sec"] = cell_timeout_sec
        if "nbconvert" in notebook_runner:
            self.runner = NotebookRunnerNbConvert(**nb_runner_kwargs)
        elif "selenium" in notebook_runner:
            if active_jupyter_backend:
                nb_runner_kwargs["active_jupyter_backend"] = \
                    active_jupyter_backend
            if browser:
                nb_runner_kwargs["browser"] = browser

            self.runner = NotebookRunnerSelenium(**nb_runner_kwargs)
        else:
            raise Exception(f"Couldn't find nb runner '{self.nb_runner}'")

        # Renames the 'runTest' method to the notebook filename (readability)
        setattr(self, self.notebook_file_name_no_ext, self.runTest)
        super().__init__(**kwargs, methodName=self.notebook_file_name_no_ext)

    def runTest(self):
        """The actual test that runs for checking the notebook"""
        log.info("Testing notebook {}".format(self.notebook_file_name_no_ext))
        result = self.runner.run_notebook()
        self._check_notebook_for_errors(result.output_ipynb_path)

        #If we're reached here, we've passed
        msg = "Notebook {nb_name} passed!\n{nb_links_text}\n-----\n".format(
              nb_name = self.notebook_file_name_no_ext,
              nb_links_text = self._get_nb_links_text())
        print(msg)
        log.debug(msg)

    def _check_notebook_for_errors(self, notebook_file_path):
        """If the output notebook has any errors, fail the test"""
        with open(notebook_file_path, "r",
                  encoding="utf-8") as output_file:
            nb = nbformat.read(output_file, nbformat.current_nbformat)
            self.errors = [output for cell in nb.cells if "outputs" in cell
                           for output in cell["outputs"]\
                           if output.output_type == "error"]
            log.debug("Notebook {} errs: {}".format(
                self.notebook_file_name_no_ext,
                self.errors))
            self.assertEqual(len(self.errors), 0, self._get_failure_message())

    def _get_failure_message(self):
        return "Notebook {nb_name} ran with {num_errors} errors. {nb_links}"\
               "".format(nb_name=self.notebook_file_name_no_ext,
                         num_errors=len(self.errors),
                         nb_links=self._get_nb_links_text())

    def _get_nb_links_text(self):
        """Create links generated from the jenkins job for readability"""
        if self.jenkins_job_url:
            return "You can view the output notebook in a web browser here: "\
                    "{jenkins_html_link} , or download the executed notebook"\
                    " here: {jenkins_nb_link}".format(
                    jenkins_html_link=self._assemble_jenkins_html_link(),
                    jenkins_nb_link=self._assemble_jenkins_nb_link())
        else:
            return ""

    def _assemble_jenkins_html_link(self):
        return self.jenkins_job_url + "ExecutedNotebooks/" + \
                self.notebook_file_name_no_ext + ".html"

    def _assemble_jenkins_nb_link(self):
        return self.jenkins_job_url+"artifact/"+"geosaurus/"+"automation/"+\
                "staging/" + self.notebook_file_name_no_ext + ".ipynb"
