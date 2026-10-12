@echo off
title Restore Project from GitHub

cd /d "%~dp0"

echo ========================================
echo   Restore Project from GitHub
echo ========================================
echo.

echo WARNING: This will restore the project from GitHub
echo All local changes will be lost
echo.
set /p confirm="Continue? [Y/N]: "

if /i not "%confirm%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Step 1: Fetching from GitHub...
git fetch origin
if %errorlevel% neq 0 (
    echo ERROR: Failed to fetch from GitHub
    pause
    exit /b 1
)

echo.
echo Step 2: Resetting to origin/main...
git reset --hard origin/main
if %errorlevel% neq 0 (
    echo ERROR: Failed to reset
    pause
    exit /b 1
)

echo.
echo Step 3: Cleaning untracked files...
git clean -fdx
if %errorlevel% neq 0 (
    echo WARNING: Some files could not be cleaned
)

echo.
echo ========================================
echo SUCCESS: Project restored!
echo ========================================
echo.
echo You can now run: startfresh.bat
echo.

pause
