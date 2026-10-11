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
if exist "startfresh.bat" (
    call "%~dp0startfresh.bat"
) else if exist "setup.bat" (
    call "%~dp0setup.bat"
) else (
    echo ERROR: Neither startfresh.bat nor setup.bat found
    echo.
    pause
)
goto main

:update
echo.
echo ========================================
echo   Updating from GitHub
echo ========================================
echo.

if exist ".git" (
    echo Git repository found, pulling changes...
    echo.
    git pull origin main
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo   SUCCESS: Updated successfully!
        echo ========================================
    ) else (
        echo.
        echo ========================================
        echo   WARNING: Update had conflicts
        echo ========================================
        echo.
        echo Trying automatic merge...
        git pull origin main --no-edit
        if %errorlevel% equ 0 (
            echo.
            echo SUCCESS: Resolved automatically
        ) else (
            echo.
            echo ERROR: Could not resolve conflicts
            echo Your local changes may be lost
            echo.
            set /p force="Force update from GitHub? [Y/N]: "
            if /i "!force!"=="Y" (
                echo Forcing update...
                git reset --hard origin/main
                echo Updated successfully
            )
        )
    )
) else (
    echo No Git repository found.
    echo Setting up Git for first time...
    echo.

    git init
    if errorlevel 1 (
        echo ERROR: Git is not installed
        echo Please install Git from: https://git-scm.com/
        pause
        goto main
    )

    echo Adding GitHub repository...
    git remote add origin https://github.com/Fo2shh/alf_hana.git

    echo Fetching updates...
    git fetch origin

    echo Setting up main branch...
    git checkout -b main
    git branch --set-upstream-to=origin/main main

    echo Pulling latest changes...
    git pull origin main --no-edit

    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo   SUCCESS: Project updated!
        echo ========================================
    ) else (
        echo.
        echo ERROR: Failed to update
        echo Please check your internet connection
    )
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
