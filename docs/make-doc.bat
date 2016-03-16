sphinx-apidoc -o apidoc -e -F -H arcgis -A Esri -V 0.1 -R 0.1 ..\src
cd apidoc
make html

