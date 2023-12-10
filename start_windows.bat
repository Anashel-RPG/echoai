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
python -m pip install pygame
python -m pip install watchdog
python -m pip install Pillow
python -m pip install requests
python -m pip install scikit-learn
python -m pip install openai
python -m pip install piexif

REM Check if last command was successful
if %errorlevel% neq 0 (
    echo Failed to install required dependencies. Exiting.
    pause
    exit /b %errorlevel%
)

REM Launching main application
echo Launching main application...
python main.py

REM Keep the window open after the script execution
pause

REM Deactivate the virtual environment on completion
call %VENV_DIR%\Scripts\deactivate.bat
