@echo off
echo "Adding conda to sys path"
path=%path%;C:\Users\atma6951\AppData\Local\Continuum\Anaconda3\Scripts

echo "Activating environment"
call activate dinotests

echo "Running tests"
Python %1\unittests\run_test_cases.py %1\unittests
echo "End of tests"

echo "Deactivating environment"
call deactivate