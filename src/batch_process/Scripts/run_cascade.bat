@echo off

:: Activate the cascade virtual environment
CALL "C:\miniforge3\Scripts\activate.bat" cascade

:: Run the cascade script
set script_dir=%~dp0

set src_dir=%script_dir%..\..\

cd "%src_dir%\run_cascade"
python run_cascade_script.py

:: Run the second script again bc it failes the first time
python run_cascade_script.py

:: Deactivate the second environment
CALL conda deactivate

:: Activate the plotting virtual environment
@REM CALL "C:\miniforge3\Scripts\activate.bat" data_env

@REM cd "%src_dir%\plotting"
@REM :: Run the plotting script 
@REM python -m plotting_constants



:: keep terminal open 'pause'