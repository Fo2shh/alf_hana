@echo off
title Quick Update from GitHub

cd /d "%~dp0"

echo ========================================
echo   Quick Update from GitHub
echo ========================================
echo.

echo Step 1: Checking if critical files are tracked...
if not exist ".git" (
    echo ERROR: This is not a Git repository
    echo.
    echo Please run restore_project.bat instead
    pause
    exit /b 1
)

git ls-files manage.py >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Critical files are not tracked in Git
    echo Using git clean would delete your project files!
    echo.
    echo SAFER APPROACH: Using git reset instead...
    echo.

    git fetch origin
    git reset --hard origin/main

    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo SUCCESS: Updated successfully!
        echo ========================================
    ) else (
        echo.
        echo ERROR: Failed to update
    )
    pause
    exit /b 0
)

echo Critical files are tracked, proceeding with safe update...
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
    echo WARNING: Update failed due to untracked files
    echo Cleaning only untracked files (not tracked ones)...
    echo.

    git clean -df
    git pull

    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo SUCCESS: Updated successfully after cleaning!
        echo ========================================
    ) else (
        echo.
        echo ERROR: Failed to pull even after cleaning
        echo Please run restore_project.bat instead
    )
)
echo.

pause
