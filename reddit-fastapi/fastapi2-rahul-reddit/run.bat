@echo off
echo ================================================================================
echo Reddit Market Opportunity Identifier
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
if not exist "venv\Lib\site-packages\requests\" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Run the application
echo Starting application...
echo.
python main.py

REM Deactivate virtual environment
deactivate

echo.
echo ================================================================================
echo Session ended. Press any key to exit.
pause >nul
