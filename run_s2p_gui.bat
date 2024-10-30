@echo off

:: Activate the s2p environment
CALL "C:\Users\Justus\Anaconda3\Scripts\activate.bat" suite2p

python C:\Users\Justus\Documents\GitHub\suite_cascade1p_ju\jd_s2p_gui.py

:: Deactivate the environment
CALL conda deactivate

pause