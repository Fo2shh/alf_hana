@echo off
title Shark Kitchen Launcher

cd /d "%~dp0"

:main
cls
echo ========================================
echo   Shark Kitchen Launcher
echo ========================================
echo.

if not exist "manage.py" (
    echo ERROR: Project not found
    echo.
    echo Make sure this file is in the project root folder
    echo.
    pause
    exit /b 1
)

echo Options:
echo.
echo 1 - Install / Setup
echo 2 - Update from GitHub
echo 3 - Run Project
echo 4 - Open Browser
echo 5 - Exit
echo.

set /p choice="Choose option (1-5): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto update
if "%choice%"=="3" goto run
if "%choice%"=="4" goto browser
if "%choice%"=="5" goto end

echo Invalid option!
pause
goto main

:install
echo.
echo Running setup...
if exist "setup.bat" (
    call "%~dp0setup.bat"
) else (
    echo ERROR: setup.bat not found
    echo.
    pause
)
goto main

:update
echo.
echo Checking for updates...
git pull
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Updated successfully!
) else (
    echo.
    echo ERROR: Update failed
)
echo.
pause
goto main

:run
echo.
echo Starting project...
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    start /B python manage.py runserver >nul 2>&1
) else (
    start /B python manage.py runserver >nul 2>&1
)

echo.
echo Waiting for server to start...
timeout /t 3 >nul

echo Opening browser...
start "" http://127.0.0.1:8000

echo.
echo Server is running
echo Press any key to stop the server...
pause

echo.
echo Stopping server...
taskkill /F /IM python.exe >nul 2>&1
goto main

:browser
echo.
echo Opening browser...
start "" http://127.0.0.1:8000
echo.
echo Browser opened
echo.
pause
goto main

:end
cls
echo.
echo Thank you for using Shark Kitchen Launcher
echo.
timeout /t 2 >nul
exit
