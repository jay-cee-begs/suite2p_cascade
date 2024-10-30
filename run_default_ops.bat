@echo off

:: Activate the first virtual environment, evt. use Activate.ps1

CALL "C:\Users\Justus\Anaconda3\Scripts\activate.bat" suite2p

:: Run the default ops script

python C:\Users\Justus\Documents\GitHub\suite_cascade1p_ju\jd_default_ops.py

:: Deactivate the first environment
CALL conda deactivate