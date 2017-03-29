@echo off

echo "Running tests"
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\Python.exe" %1\unittests\run_test_cases.py %1\unittests
echo "End of tests"
