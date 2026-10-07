# Alfhana Kitchen - Quick Start Guide

This project includes a convenient `start.bat` script that makes it easy to set up and run the Alfhana Kitchen management system on any Windows machine.

## Quick Setup

The script has three modes:

### 1. Quick Download & Setup (--silent mode)

Double-click `start.bat` to run in normal mode, or run with `--silent` flag to skip confirmations:

```batch
start.bat --silent
```

This mode will:
- Download the project from GitHub if not present
- Create virtual environment
- Install dependencies
- Run migrations
- Start the server

### 2. Clone Only (--clone-only mode)

If you just want to download the project without running setup:

```batch
start.bat --clone-only
```

### 3. Local Setup

If the project already exists locally:

1. Open Command Prompt in the project directory
2. Run `start.bat` (normal mode)
3. The script will detect the existing project and continue with setup

## Manual Setup Steps

If you prefer manual setup:

```batch
git clone https://github.com/Fo2shh/alf_hana.git
cd alfhana_kitchen
start.bat
```

## Project Structure

```
alfhana_kitchen/
├── alfhana_kitchen/          # Django settings
├── core/                     # Core application
├── orders/                   # Orders application
├── media/                    # Uploaded files
├── staticfiles/              # Static assets
├── db.sqlite3                # Database (will be created)
├── README.md                 # This file
└── start.bat                 # Auto-setup script
```

## After Setup

- Access the application at: `http://127.0.0.1:8000`
- Default credentials:
  - Admin: `admin` / `admin123`
  - Kitchen: `kitchen` / `kitchen123`
  - Driver: `driver1` / `driver123`
- Press Ctrl+C in the terminal to stop the server

## Requirements

- Windows (Git, Python 3.8+)
- Internet connection (for first-time download)
