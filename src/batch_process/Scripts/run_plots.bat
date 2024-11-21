@echo off

:: Activate the data_env virtual environment
CALL "C:\Users\Justus\miniforge3\Scripts\activate.bat" data_env

:: Run the plotting script 
python -m plotting_constants

:: keep terminal open 
pause