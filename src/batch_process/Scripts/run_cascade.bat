@echo off

:: Activate the cascade virtual environment
CALL "C:\Users\Justus\miniforge3\Scripts\activate.bat" cascade

:: Run the cascade script
set script_dir=%~dp0

set src_dir=%script_dir%..\..\

cd "%src_dir%\run_cascade"
python -m cascade_deconvolve

:: Run the second script again bc it failes the first time
python -m cascade_deconvolve

:: Deactivate the second environment
CALL conda deactivate

:: Activate the plotting virtual environment
CALL "C:\Users\Justus\miniforge3\Scripts\activate.bat" data_env

cd "%src_dir%\plotting"
:: Run the plotting script 
python -m plotting_constants



:: keep terminal open 'pause'