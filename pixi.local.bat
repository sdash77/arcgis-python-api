python -m pip install .\src --no-deps

REM Install arcgis-mapping if available
IF EXIST "..\geoserpent" (
    where npm >nul 2>nul
    IF %ERRORLEVEL% EQU 0 (
        python -m pip install ..\geoserpent\arcgis-mapping\src --no-deps
    )
)
