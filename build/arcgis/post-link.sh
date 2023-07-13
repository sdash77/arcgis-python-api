"${PREFIX}/bin/python" -m arcgis.install --remove  >> "${PREFIX}/.messages.txt" 2>&1

err_msg="jupyter nbextension command failed: map widgets in the jupyter notebook may not work, installation continuing..."

if [ -f "${PREFIX}/bin/jupyter-nbextension" ];
then
	if ! "${PREFIX}/bin/jupyter-nbextension" install --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
		then echo "$err_msg" >> "${PREFIX}/.messages.txt"
	fi

	if ! "${PREFIX}/bin/jupyter-nbextension" enable  --py --sys-prefix arcgis >> "${PREFIX}/.messages.txt" 2>&1
		then echo "$err_msg" >> "${PREFIX}/.messages.txt"
	fi
else
	echo ${err_msg}
fi
