@echo off

CALL "C:\Users\jcbegs\miniforge3\Scripts\activate.bat" cascade

:: Run the second script
set script_dir=%~dp0

set src_dir=%script_dir%..\..\

cd "%src_dir%\run_cascade"
python -m cascade_deconvolve

:: Run the second script again bc it failes the first time
python -m cascade_deconvolve