@echo off

:: Activate the first virtual environment, evt. use Activate.ps1

CALL "C:\miniforge3\Scripts\activate.bat" suite2p

python -c "import sys; print('Python executable:', sys.executable); print('sys.path:', sys.path)"

@REM Saving directory of batch file
set script_dir=%~dp0

cd "%script_dir%..\"

:: Run the default ops script

python -m jd_default_ops

:: Deactivate the first environment
CALL conda deactivate