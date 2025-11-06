@echo off
echo 🚀 Daily Brief Service - Quick Deploy Script
echo ==========================================
echo.

:: Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found!
    echo Please run this script from the reminderAPP directory
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error creating virtual environment
        echo Make sure Python 3.11+ is installed
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error installing dependencies
    pause
    exit /b 1
)

:: Check if .env exists
if not exist ".env" (
    echo ⚙️  Setting up configuration...
    copy .env.example .env
    echo.
    echo 📝 IMPORTANT: Edit .env file with your email credentials!
    echo Required settings:
    echo   EMAIL_ADDRESS=your-email@gmail.com
    echo   EMAIL_PASSWORD=your-app-password
    echo   IMAP_HOST=imap.gmail.com
    echo   SMTP_HOST=smtp.gmail.com
    echo.
    echo Opening .env file for editing...
    notepad .env
    echo.
    pause
)

:: Test configuration
echo 🧪 Testing configuration...
set /p test_email="Enter your email for test (or press Enter to skip): "
if not "%test_email%"=="" (
    python app.py --send-test %test_email%
    if errorlevel 1 (
        echo ❌ Configuration test failed
        echo Please check your .env settings
        pause
        exit /b 1
    )
    echo ✅ Test email sent successfully!
)

:: Ask how to run
echo.
echo 🎯 Choose deployment mode:
echo 1. Run normally (show logs, keep window open)
echo 2. Test mode (dry-run, no emails sent)
echo 3. Create Windows startup task
set /p mode="Enter choice (1-3): "

if "%mode%"=="1" (
    echo 🚀 Starting Daily Brief Service...
    echo Press Ctrl+C to stop
    python app.py
) else if "%mode%"=="2" (
    echo 🧪 Starting in test mode...
    echo Press Ctrl+C to stop
    python app.py --dry-run
) else if "%mode%"=="3" (
    echo 📋 Creating Windows startup task...
    echo.
    echo Copy this command to Task Scheduler:
    echo Program: %cd%\venv\Scripts\python.exe
    echo Arguments: app.py
    echo Start in: %cd%
    echo.
    pause
) else (
    echo Invalid choice, starting normally...
    python app.py
)

echo.
echo 🎉 Daily Brief Service deployment complete!
pause