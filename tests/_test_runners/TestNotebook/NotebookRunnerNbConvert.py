import sys
import os
import unittest
import logging
log = logging.getLogger()

from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat

from _test_runners.TestNotebook.NotebookRunnerResult \
    import NotebookRunnerResult

class NotebookRunnerNbConvert:
    def __init__(self, notebook_file_path, output_dir, cell_timeout_sec=300,
                 *args, **kwargs):
        self.cell_timeout_sec = cell_timeout_sec
        self.input_notebook_file_path = notebook_file_path

        self.notebook_file_name_no_ext = os.path.splitext(os.path.basename(
            self.input_notebook_file_path))[0]
        self.output_ipynb_path = os.path.join(output_dir,
            self.notebook_file_name_no_ext + ".ipynb")
        self.output_html_path = os.path.join(output_dir,
            self.notebook_file_name_no_ext + ".html")

    def run_notebook(self):
        """Execute a notebook via nbconvert, save the output as both a 
        notebook and an HTML file in the output_dir

        Returns an object with these attributes
        """
        with open(self.input_notebook_file_path, "r",
                  encoding="utf-8") as input_nb_file:
            #Execute input notebook
            input_nb = nbformat.read(input_nb_file,
                as_version=nbformat.current_nbformat)
            ep = ExecutePreprocessor(timeout=self.cell_timeout_sec,
                                     allow_errors=True,
                                     kernel_name="python3")
            ep.preprocess(input_nb, {})

            #Write outputted notebook to file on disk as notebook
            with open(self.output_ipynb_path, "wt",
                      encoding="utf-8") as output_nb_file:
                nbformat.write(input_nb, output_nb_file,
                               version=nbformat.current_nbformat)

            #Write outputted notebook to file on disk as html
            html_exporter = HTMLExporter()
            (body, resources) = html_exporter.from_notebook_node(input_nb)
            with open(self.output_html_path, "w",
                      encoding="utf-8") as output_html:
                      output_html.write(body)

        # Return the paths to the output ipynb and html files
        return NotebookRunnerResult(output_ipynb_path = self.output_ipynb_path,
                                    output_html_path = self.output_html_path)
