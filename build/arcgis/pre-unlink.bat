"%PREFIX%\Scripts\jupyter-nbextension.exe" disable   --py --sys-prefix arcgis  >> "%PREFIX%/.messages.txt" 2>&1
"%PREFIX%\Scripts\jupyter-nbextension.exe" uninstall --py --sys-prefix arcgis  >> "%PREFIX%/.messages.txt" 2>&1
