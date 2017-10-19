.\buildarcgis.bat %*

REM for each file converted for win-64, upload it to conda
for /r %%i in (___output\win-64\arcgis*) do (
    anaconda upload %%i
)

REM for each file converted for win-32, upload it to conda
for /r %%i in (___output\win-32\arcgis*) do (
    anaconda upload %%i
)

REM for each file converted for linux-64, upload it to conda
for /r %%i in (___output\linux-64\arcgis*) do (
    anaconda upload %%i
)
