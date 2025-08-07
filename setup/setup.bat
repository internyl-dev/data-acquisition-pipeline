@echo off
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found. Please install Python 3.x from https://www.python.org/downloads/
    goto :eof
)

echo Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Terminating...
    goto :eof
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment. Terminating...
    goto :eof
)

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Terminating...
    goto :eof
)

echo Installing Playwright browser drivers...
playwright install
if %errorlevel% neq 0 (
    echo Failed to install Playwright browsers. Terminating...
    goto :eof
)

echo Setup complete!
pause
