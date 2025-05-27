@echo off
REM RSS Feed Processor - Daily Production Run
REM Schedule this batch file to run daily for automated news digest

echo.
echo 🚀 RSS FEED PROCESSOR - DAILY PRODUCTION RUN
echo ================================================================
echo ⏰ Started at: %DATE% %TIME%
echo.

REM Change to the project directory
cd /d "C:\Projects\agents\product_reader"

REM Verify we're in the right location
if not exist "src\main.py" (
    echo ❌ Error: Cannot find RSS Feed Processor files
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo 📡 Running RSS Feed Processor...
python src/main.py --days 1

REM Check if the process was successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ RSS Feed Processor completed successfully!
    echo 📧 Daily digest has been sent
) else (
    echo.
    echo ❌ RSS Feed Processor failed with error code: %ERRORLEVEL%
    echo 📋 Check logs for details
)

echo.
echo ⏰ Completed at: %DATE% %TIME%
echo 🎯 Next run: Tomorrow at the same time
echo ================================================================

REM Uncomment the line below if you want to see output when running manually
REM pause
