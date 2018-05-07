import sys
import os
import unittest
import logging
log = logging.getLogger()

from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat

class TestNotebook(unittest.TestCase):
    """Given a notebook file, run it and output the ran notebook as HTML.
    Check the notebook for any errors in the python code's execution
    (unhandled exceptions, if output_type == "error"), fail the test if so.
    """
    def __init__(self, notebook_file_path, output_dir, notebook_timeout, 
                 jenkins_job_url=None, **kwargs):
        """notebook_file_path is the path to the notebook to test
        output_dir is where all ran notebooks and converted html go to
        notebook_timeout is the max number of seconds a CELL in a nb can run
        jenkins_job_url is optional, it is used to print out a link to the
        outputted notebook if the test notebook suite is running on Jenkins
        """
        self.input_notebook_file_path = notebook_file_path
        self.output_dir = output_dir
        self.notebook_timeout = notebook_timeout
        self.jenkins_job_url = jenkins_job_url
        self.notebook_file_name_no_ext = os.path.splitext(os.path.basename(
            self.input_notebook_file_path))[0]
        self.output_notebook_file_path = os.path.join(self.output_dir,
            self.notebook_file_name_no_ext + ".ipynb")
        self.output_notebook_html_file_path = os.path.join(self.output_dir,
            self.notebook_file_name_no_ext + ".html")

        #Renames the 'runTest' method to the notebook filename (readability)
        setattr(self, self.notebook_file_name_no_ext, self.runTest)
        super().__init__(**kwargs, methodName=self.notebook_file_name_no_ext)

    def runTest(self):
        """The actual test that runs for checking the notebook"""
        log.info("Testing notebook {}".format(self.notebook_file_name_no_ext))
        self._run_input_notebook_convert_to_html(self.notebook_timeout)
        self._check_output_notebook_for_errors()
        
        #If we're reached here, we've passed
        msg = "Notebook {nb_name} passed!\n{nb_links_text}\n-----\n".format(
              nb_name = self.notebook_file_name_no_ext,
              nb_links_text = self._get_nb_links_text())
        print(msg)
        log.debug(msg)

    def _run_input_notebook_convert_to_html(self, timeout):
        """Execute a notebook via nbconvert, save the output as both a 
        notebook and an HTML file in the output_dir
        """
        with open(self.input_notebook_file_path, "r",
                  encoding="utf-8") as input_nb_file:
            #Execute input notebook
            input_nb = nbformat.read(input_nb_file,
                as_version=nbformat.current_nbformat)
            ep = ExecutePreprocessor(timeout=timeout,
                                     allow_errors=True,
                                     kernel_name="python3")
            ep.preprocess(input_nb, {})

            #Write outputted notebook to file on disk as notebook
            with open(self.output_notebook_file_path, "wt",
                      encoding="utf-8") as output_nb_file:
                nbformat.write(input_nb, output_nb_file,
                    version=nbformat.current_nbformat)

            #Write outputted notebook to file on disk as html
            html_exporter = HTMLExporter()
            (body, resources) = html_exporter.from_notebook_node(input_nb)
            with open(self.output_notebook_html_file_path, "w",
                      encoding="utf-8") as output_html:
                output_html.write(body)

    def _check_output_notebook_for_errors(self):
        """If the output notebook has any errors, fail the test"""
        with open(self.output_notebook_file_path, "r",
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
