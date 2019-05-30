# Tests

This directory contains everything needed to run tests on various parts of the Python API.

## Useage

To run all unit tests and all sanity tests:

`python run_tests.py --unit --sanity`

To run one specific unit test:

`python run_tests.py --unit ./unit/test_arcgis/../foo.py`

To run one specific integration test:

`python run_tests.py --integration ./integration/../foo.py`

To run a specific suite file of tests:

`python run_tests.py --suite /path/to/suite.yaml`

You can glob paths to test multiple files. For example, to run all tests in the `./unit/foobar/` folder, you would run:

`python run_tests.py --unit ./unit/foobar/*.py`

## ./unit

> Unit Test: A test written by a programmer for the purpose of ensuring that the production code does what the programmer expects it to do.

Source: https://blog.cleancoder.com/uncle-bob/2017/05/05/TestDefinitions.html

A unit test should test the smallest amount of code possible. In `geosaurus`'s case, it should assert the logic of some code __without__ connecting to an external system. This means your unit tests should __not__ connect to a portal, should __not__ call into a 3rd party python library, etc.

 __All unit tests in `./unit` have network access blocked__. If you find that you need network access to write a test, you should either 1) mock out the code/the response of the network call or 2) move the test to `./integration/`.

## ./integration

> Integration Test: A test written by architects and/or technical leads for the purpose of ensuring that a sub-assembly of system components operates correctly. 

Source: https://blog.cleancoder.com/uncle-bob/2017/05/05/TestDefinitions.html

An integration test covers most other cases outside of unit tests. As we define it, it asserts end-user functionality when calling public-facing APIs. These tests can connect external systems, connect to Portals, call into 3rd party libraries, etc.

## ./notebook

This directory contains any `.ipynb` files we want to test as a part of any suite. Notebooks can be run with two different "runners": an `nbconvert` runner (headless, no widget output), and a `selenium` runner (runs in a web browser, widget output in HTML). See the `./suite` section for more information how notebooks are run.

## ./utils

Place any code you want to use across multiple tests in this module (mock classes, certain assert logic, helper functions, etc). You can import it via `import utils`, `from utils.mocks import foo`, etc.

## ./widget

Contains all the notebooks and javascript code to test the `arcgis-map-ipywidget` functionality.

## ./sanity

Self explantory, tests that basic imports of all modules and submodules don't fail, other basic tests.

## ./\_suites/

The .yaml files in this directory represent what is run for our CI/CD systems on pull request, as a regression test, as a full nightly suite, etc. You can make your own .yaml file if you'd like to run a certain mixture of different tests. Here's how the file is formatted for reference:

There are 6 top level keys:

    - `unit_tests_to_run`
    - `sanity_tests_to_run`
    - `integration_tests_to_run`
    - `nbconvert_notebook_tests_to_run`
        - Run these notebooks using the `nbconvert` as a backend (no browser is opened to run the notebook, no javascript is ran. There is no map widget output)
    - `selenium_notebook_tests_to_run`
        - Run these notebooks using `selenium` as a backend. You need both the Python selenium package and the `Chrome`/`Firefox` selenium driver standalone executables.
    - `widget_unit_tests_to_run`

The value on each key is an object which itself contains two keys:

    - `config`
    - `paths`

`paths` is the most important part of this file. It contains a list of strings, with each string representing a [glob](https://docs.python.org/2/library/glob.html)-able path to files (it is run via `glob.glob(<path>, recursive=True)`. You don't need to glob, you can use absolute paths if you want.

For any path contained in the `geosaurus` repository, start out your string with `{geosaurus_dir}/path/to/whatever` and it will sub in your path to geosaurus. Use unix-style `/` even if you're on a windows machine. `{arcgis_python_api_dir}` isn't accessible when running from cmd line in this directory, it's used by the CI/CD system and some scripts in `geosaurus/automation`.

`config` contains miscellaneous specific options for those tests, such as 

    - `blacklist` (list of glob-able paths to remove from `paths` if there is a match)
    - `cell_timeout_sec` (if the test is a notebook test, how long to wait in seconds for a cell to finish before forcing a failure)
    - `browser` (if the test is a selenium notebook test, whether to override to use Firefox or Chrome. If not specified, will pick one depending on the day of the week)

## ./\_test\_runners

This directory contains all the Python code needed to run the specified unit/notebook/etc. tests and output the XML to the correct location

