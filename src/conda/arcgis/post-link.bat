"%PREFIX%\python.exe" -m arcgis.install --remove  >> "%PREFIX%/.messages.txt" 2>&1
"%PREFIX%\Scripts\jupyter-nbextension.exe" install --py --sys-prefix arcgis  >> "%PREFIX%/.messages.txt" 2>&1
"%PREFIX%\Scripts\jupyter-nbextension.exe" enable  --py --sys-prefix arcgis  >> "%PREFIX%/.messages.txt" 2>&1
