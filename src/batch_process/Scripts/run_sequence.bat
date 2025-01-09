@echo off

:: Activate the first virtual environment, evt. use Activate.ps1

CALL "C:\miniforge3\Scripts\activate.bat" suite2p
:: Run the first script

set script_dir=%~dp0

set src_dir=%script_dir%..\..\

cd "%src_dir%\run_suite2p"
python run_suite2p.py

:: Deactivate the first environment
CALL conda deactivate

:: Activate the second virtual environment
CALL "C:\miniforge3\Scripts\activate.bat" cascade

cd "%src_dir%\run_cascade"
python run_cascade_script.py

:: Run the second script again bc it failes the first time
python run_cascade_script.py

:: Deactivate the second environment
CALL conda deactivate

@REM :: Activate the third virtual environment
@REM CALL "C:\miniforge3\Scripts\activate.bat" data_env

@REM cd "%src_dir%\plotting"
@REM :: Run the third script 
@REM python -m plotting_constants



:: keep terminal open 'pause'
