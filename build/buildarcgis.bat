ren ___output ___output.old
mkdir ___output

REM If version was not passed as command line arg then use a default one
SET ver=%1
if "%~1"=="" SET ver=1.2.6

conda build --py 3.6 arcgis --output-folder ___output
conda build --py 3.5 arcgis --output-folder ___output

REM for each file generated from the above commands
for /r %%i in (___output\win-64\arcgis*) do (
    REM run the convert command on each of those files
    conda convert -f -p win-32 %%i -o ___output
    conda convert -f -p linux-64 %%i -o ___output
)
