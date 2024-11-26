@echo off

:: Activate the data_env virtual environment
CALL "C:\Users\jcbegs\miniforge3\Scripts\activate.bat" plt_analysis

python -c "import sys; print('Python executable:', sys.executable); print('sys.path:', sys.path)"

@REM Saving directory of batch file
set script_dir=%~dp0
echo script_dir is %script_dir% 
set src_dir=%script_dir%..\..\

echo src_dir is %src_dir%

cd "%src_dir%\plotting"

echo current directory is %cd%

:: Run the plotting script 
python -m plotting_constants

:: keep terminal open 
pause