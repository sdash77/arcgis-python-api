
"${PREFIX}/bin/jupyter-nbextension" disable   --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
"${PREFIX}/bin/jupyter-nbextension" uninstall --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
