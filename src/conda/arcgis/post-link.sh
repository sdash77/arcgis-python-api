"${PREFIX}/bin/jupyter-nbextension" install --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
"${PREFIX}/bin/jupyter-nbextension" enable  --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
