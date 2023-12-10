@echo off

REM Set the directory for the virtual environment
set VENV_DIR=venv

REM Check if the virtual environment directory exists
if not exist "%VENV_DIR%" (
    echo Creating a new virtual environment...
    python -m venv %VENV_DIR%
)

REM Activate the virtual environment
call %VENV_DIR%\Scripts\activate.bat

REM Checking and installing required packages
echo Checking and installing required packages...
python -m pip install --upgrade pip
pip install pygame
pip install watchdog
pip install Pillow
pip install requests
pip install scikit-learn
pip install openai
pip install piexif

REM Check if last command was successful
if %errorlevel% neq 0 (
    echo Failed to install required dependencies. Exiting.
    pause
    exit /b %errorlevel%
)

REM Launching main application
echo Launching main application...
python ranking.py

REM Keep the window open after the script execution
pause

REM Deactivate the virtual environment on completion
call %VENV_DIR%\Scripts\deactivate.bat
