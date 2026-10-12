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
    echo Project not found in current folder.
    echo.
    echo Options:
    echo.
    echo 1 - Download project from GitHub
    echo 2 - Exit
    echo.
    set /p no_project_choice="Choose option: "

    if "%no_project_choice%"=="1" goto download
    if "%no_project_choice%"=="2" goto end

    echo Invalid option!
    pause
    goto main
)

echo Options:
echo.
echo 1 - Install / Setup
echo 2 - Update from GitHub
echo 3 - Add Menu Items (seed_menu)
echo 4 - Run Project
echo 5 - Exit
echo.
set /p choice="Choose option: "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto update
if "%choice%"=="3" goto seed_menu
if "%choice%"=="4" goto run
if "%choice%"=="5" goto end

echo Invalid option!
pause
goto main

:download
echo.
echo Downloading project from GitHub...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://github.com/Fo2shh/alf_hana/archive/refs/heads/main.zip'; $output = 'alf_hana.zip'; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing"
if %errorlevel% neq 0 (
    echo ERROR: Failed to download
    pause
    goto main
)
echo Downloaded!
echo Extracting...
powershell -Command "Expand-Archive -Path 'alf_hana.zip' -DestinationPath '.' -Force"
del "alf_hana.zip" >nul 2>&1
xcopy /E /I /Y "alf_hana-main\*" "." >nul
rmdir /S /Q "alf_hana-main" >nul 2>&1
echo Done! Now run option 1.
pause
goto main

:install
echo.
echo Installing...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    pause
    goto main
)
if not exist "venv" python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul
python manage.py migrate >nul
python manage.py collectstatic --noinput >nul
if exist "create_admin.py" python create_admin.py
echo Setup complete!
echo Login: admin / admin123
pause
goto main

:seed_menu
echo.
echo Adding menu items...
if not exist "manage.py" (
    echo ERROR: manage.py not found
    pause
    goto main
)
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
if exist "seed_menu.py" (
    python manage.py seed_menu
    if errorlevel 1 (
        echo ERROR: Failed to add menu items
        pause
        goto main
    )
    echo Menu items added successfully!
) else (
    echo ERROR: seed_menu.py not found
    echo This file should be in the project folder
)
pause
goto main

:update
echo.
echo Updating...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://github.com/Fo2shh/alf_hana/archive/refs/heads/main.zip'; $output = 'alf_hana.zip'; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing"
if %errorlevel% neq 0 (
    echo ERROR: Failed to download
    pause
    goto main
)
echo Downloaded!
echo Extracting...
powershell -Command "Expand-Archive -Path 'alf_hana.zip' -DestinationPath '.' -Force"
del "alf_hana.zip" >nul 2>&1
xcopy /E /I /Y "alf_hana-main\*" "." >nul
rmdir /S /Q "alf_hana-main" >nul 2>&1
echo Updated!
pause
goto main

:run
echo.
echo Starting...
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
start /B python manage.py runserver >nul 2>&1
timeout /t 3 >nul
start "" http://127.0.0.1:8000
echo Running. Press any key to stop...
pause
taskkill /F /IM python.exe >nul 2>&1
goto main

:end
exit
