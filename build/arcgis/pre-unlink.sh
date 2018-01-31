err_msg="jupyter nbextension command failed: map widgets may not have uninstalled correctly, installation continuing..."

if ! "${PREFIX}/bin/jupyter-nbextension" disable   --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
then echo $err_msg >> "${PREFIX}/.messages.txt"
fi

if ! "${PREFIX}/bin/jupyter-nbextension" uninstall --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
then echo $err_msg >> "${PREFIX}/.messages.txt"
fi
