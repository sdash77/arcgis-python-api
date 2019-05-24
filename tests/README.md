# Tests

This directory contains everything needed to run the different type of tests we have. To run all unit tests and all sanity tests:

`python run_tests.py --unit --sanity`

To run a specific suite of tests:

`python run_tests.py --suite /path/to/suite.yaml`

See the below section for more information on how `suite.yaml` files are structured.

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

    - `blacklist_regexes` (list of regex strings to test against all file paths of test files, and to remove if there is a match)
    - `cell_timeout_sec` (if the test is a notebook test, how long to wait in seconds for a cell to finish before forcing a failure)
    - `browser` (if the test is a selenium notebook test, whether to override to use Firefox or Chrome. If not specified, will pick one depending on the day of the week)
