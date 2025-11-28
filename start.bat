@echo off
echo 🎯 Starting Rank Tracker Prototype...

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found. Creating...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install/update dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please configure your API keys!
    echo 📝 Edit the .env file with your DataForSEO and geocoding credentials
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start the application
echo 🚀 Starting server on http://127.0.0.1:8000
echo 📊 API Documentation: http://127.0.0.1:8000/docs
echo 🔄 Ctrl+C to stop the server
echo.

python main.py