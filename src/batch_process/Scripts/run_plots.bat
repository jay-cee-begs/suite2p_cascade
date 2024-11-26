@echo off

:: Activate the data_env virtual environment
CALL "C:\miniforge3\Scripts\activate.bat" data_env

@REM Saving directory of batch file
set script_dir=%~dp0

set src_dir = %script_dir%..\..\

cd "%src_dir%\plotting"

:: Run the plotting script 
python -m plotting_constants

:: keep terminal open 
pause