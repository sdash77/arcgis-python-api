import os
import requests
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from parameterized import parameterized
import unittest
import warnings

warnings.filterwarnings("ignore")

BASE_URL = "https://raw.githubusercontent.com/Esri/arcgis-python-api/master/samples/04_gis_analysts_data_scientists/"
NOTEBOOK_DIR = os.environ.get("NOTEBOOK_DIR")

NOTEBOOKS = [
    {
        "name": "land_cover_classification_using_sparse_training_data",
        "owner": "spathak",
    },
]

RESULT_FILE = "notebook_test_results.html"
CC_FILE = "notebook_cc_list.txt"
FAILED_TESTS = []
CC_EMAILS = {"ptuteja@esri.com", "sbaloni@esri.com", "sanojprasad@esri.com"}


def record_failure(test_name, owner_username):
    email = f"{owner_username}@esri.com"
    FAILED_TESTS.append(f"- {test_name}: <a href='mailto:{email}'>{email}</a><br/>")
    if email not in CC_EMAILS:
        CC_EMAILS.add(email)


if not os.path.exists(NOTEBOOK_DIR):
    os.makedirs(NOTEBOOK_DIR)


def get_notebook_names():
    return [(nb["name"], nb["owner"]) for nb in NOTEBOOKS]


def execute_nb_cell_wise(notebook_path):
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        nb.cells = [cell for cell in nb.cells if cell.cell_type == "code"]

        begin_code = "import time\nbegin=time.time()"
        end_code = 'end=time.time()\nprint(f"Time taken is {end - begin} seconds")'
        nb.cells.insert(0, nbformat.v4.new_code_cell(begin_code))
        nb.cells.append(nbformat.v4.new_code_cell(end_code))

        ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
        ep.preprocess(nb, {"metadata": {"path": NOTEBOOK_DIR}})

        with open(notebook_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        print("Processed and executed")

    except CellExecutionError as e:
        print(f"Execution error in notebook: {e}")
        raise AssertionError(
            f"Notebook execution failed:\n{e}"
        )  # Ensure the test fails
    except Exception as e:
        print(f"General error: {e}")
        raise AssertionError(f"General error during notebook execution:\n{e}")


def commonNotebookTests(nb_name, owner_username):
    notebook_file = nb_name + ".ipynb"
    notebook_path = os.path.join(NOTEBOOK_DIR, notebook_file)

    print("Test Start")
    print(f"Notebook: {notebook_file}")
    print(f"Owner: {owner_username}")

    if os.path.exists(notebook_path):
        os.remove(notebook_path)

    url = BASE_URL + notebook_file
    response = requests.get(url)
    assert response.status_code == 200
    with open(notebook_path, "wb") as f:
        f.write(response.content)

    try:
        execute_nb_cell_wise(notebook_path)
    except Exception as e:
        record_failure(nb_name, owner_username)
        raise e

    print("Test End")


class TestNotebooks(unittest.TestCase):
    @parameterized.expand(get_notebook_names())
    def test_notebook(self, nb_name, owner_username):
        commonNotebookTests(nb_name, owner_username)

    @classmethod
    def tearDownClass(cls):
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            if FAILED_TESTS:
                for line in FAILED_TESTS:
                    f.write(line + "\n")
            else:
                f.write(
                    "Jenkins notebook test job failed: Configuration error - Suraj Baloni, Sanoj Dimri."
                )
        with open(CC_FILE, "w", encoding="utf-8") as f:
            f.write(", ".join(CC_EMAILS))


if __name__ == "__main__":
    unittest.main()
