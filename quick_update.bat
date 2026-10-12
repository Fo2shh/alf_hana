@echo off
title Quick Update from GitHub

cd /d "%~dp0"

echo ========================================
echo   Quick Update from GitHub
echo ========================================
echo.

echo Step 1: Cleaning untracked files...
git clean -df
if %errorlevel% neq 0 (
    echo ERROR: Failed to clean files
    pause
    exit /b 1
)
echo Cleaned successfully
echo.

echo Step 2: Pulling changes from GitHub...
git pull
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: Updated successfully!
    echo ========================================
) else (
    echo.
    echo ERROR: Failed to pull changes
)
echo.

pause
