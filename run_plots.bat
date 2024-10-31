@echo off

:: Activate the data_env virtual environment
CALL "C:\Users\Justus\Anaconda3\Scripts\activate.bat" data_env

:: Run the plotting script 
python C:\Users\Justus\Documents\GitHub\suite_cascade1p_ju\plotting_constants.py

:: keep terminal open 
pause