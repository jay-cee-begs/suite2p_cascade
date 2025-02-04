@echo off

:: Activate the s2p environment
CALL "C:\Users\jcbeg\miniforge\Scripts\activate.bat" cascade 

:: Run the first script

set script_dir=%~dp0

@REM set src_dir=%script_dir%..\..\


cd "%script_dir%..\"


python -m cascade_settings