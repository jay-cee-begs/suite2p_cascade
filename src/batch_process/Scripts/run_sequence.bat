@echo off

:: Activate the first virtual environment, evt. use Activate.ps1

CALL "C:\miniforge3C:\Users\Justus\miniforge3\Scripts\activate.bat" suite2p
:: Run the first script

set script_dir=%~dp0

set src_dir=%script_dir%..\..\

cd "%src_dir%\run_suite2p"
python -m suite2p_detect

:: Deactivate the first environment
CALL conda deactivate

:: Activate the second virtual environment
CALL "C:\Users\Justus\miniforge3\Scripts\activate.bat" cascade

:: Run the second script
set script_dir=%~dp0

set src_dir=%script_dir%..\..\

cd "%src_dir%\run_cascade"
python -m cascade_deconvolve

:: Run the second script again bc it failes the first time
python -m cascade_deconvolve

:: Deactivate the second environment
CALL conda deactivate

:: Activate the third virtual environment
CALL "C:\Users\Justus\miniforge3\Scripts\activate.bat" data_env

cd "%src_dir%\plotting"
:: Run the third script 
python -m plotting_constants



:: keep terminal open 'pause'
