ren ___output ___output.old
mkdir ___output

REM If version was not passed as command line arg then use a default one
SET ver=%1
if "%~1"=="" SET ver=1.2.6

conda build --py 3.6 arcgis --output-folder ___output
conda build --py 3.5 arcgis --output-folder ___output

REM for each file generated from the above commands (i.e. files that end in .tar.bz2)
for /r %%file in (___output\win-64\arcgis-%ver%-*.tar.bz2) do (
    REM run the convert command on each of those files
    conda convert -f -p win-32 %%file -o ___output
)

REM for each file converted for win-64, upload it to conda
for /r %%file in (___output\win-64\arcgis-%ver%-*.tar.bz2) do (
    anaconda upload %%file
)

REM for each file converted for win-32, upload it to conda
for /r %%file in (___output\win-32\arcgis-%ver%-*.tar.bz2) do (
    anaconda upload %%file
)
