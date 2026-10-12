@echo off
title Download Project from GitHub

cd /d "%~dp0"

echo ========================================
echo   Download Project from GitHub
echo ========================================
echo.
echo This will download the project from GitHub
echo and extract it to a new folder.
echo.
echo Make sure you have internet connection.
echo.
pause

echo.
echo Downloading project from GitHub...
echo.

powershell -Command "& { $url = 'https://github.com/Fo2shh/alf_hana/archive/refs/heads/main.zip'; $output = 'alf_hana.zip'; Invoke-WebRequest -Uri $url -OutFile $output }"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to download project
    echo Please check your internet connection
    pause
    exit /b 1
)

echo Downloaded successfully!
echo.

echo Extracting files...
echo.

powershell -Command "Expand-Archive -Path 'alf_hana.zip' -DestinationPath '.' -Force"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to extract files
    pause
    exit /b 1
)

echo Extracted successfully!
echo.

echo Cleaning up...
del "alf_hana.zip"

echo Moving files to current folder...
xcopy /E /I /Y "alf_hana-main\*" "."
rmdir /S /Q "alf_hana-main"

echo.
echo ========================================
echo SUCCESS: Project downloaded!
echo ========================================
echo.
echo You can now run: startfresh.bat
echo.
pause
