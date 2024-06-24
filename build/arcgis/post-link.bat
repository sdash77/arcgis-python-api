set DISABLE_ARCGIS_LEARN=1

"%PREFIX%\python.exe" -c "import certifi, time; time.sleep(1);"  >> "%PREFIX%/.messages.txt" 2>&1

"%PREFIX%\python.exe" -m arcgis.install --remove  >> "%PREFIX%/.messages.txt" 2>&1

set DISABLE_ARCGIS_LEARN=''
