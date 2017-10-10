ren ___output ___output.old
mkdir ___output

REM If version was not passed as command line arg then use a default one
SET ver=%1
if "%~1"=="" SET ver=1.2.6

conda build --py 3.6 arcgis --output-folder ___output
conda build --py 3.5 arcgis --output-folder ___output

conda convert -f -p win-32 ___output\win-64\arcgis-%ver%-py35_1.tar.bz2 -o ___output
conda convert -f -p win-32 ___output\win-64\arcgis-%ver%-py36_1.tar.bz2 -o ___output

anaconda upload ___output\win-64\arcgis-%ver%-py36_1.tar.bz2
anaconda upload ___output\win-64\arcgis-%ver%-py35_1.tar.bz2
anaconda upload ___output\win-32\arcgis-%ver%-py36_1.tar.bz2
anaconda upload ___output\win-32\arcgis-%ver%-py35_1.tar.bz2