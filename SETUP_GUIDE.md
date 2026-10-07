# Transfer and Setup Guide for Another Computer

## Before Transfer

### Required Files
To transfer the project to another computer, make sure to copy the entire folder with all the following files:

```
alfhana_kitchen/
├── alfhana_kitchen/          # Project settings
├── core/                     # Core app
├── orders/                   # Orders app
├── media/                    # Uploaded files (optional)
├── venv/                     # Virtual Environment (optional)
├── manage.py                 # Django management file
├── requirements.txt          # Required packages
├── create_admin.py           # User creation script
├── start.bat                 # Main setup and run file
├── README.md                 # Project guide
└── SETUP_GUIDE.md            # This file
```

### Files That Can Be Excluded
To reduce project size, you can exclude:
- `venv/` (will be auto-created on new computer)
- `db.sqlite3` (will be auto-created on new computer)
- `__pycache__/` (temporary folders)
- `*.pyc` (temporary files)

## On New Computer

### Basic Requirements
1. **Python 3.8 or later**
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Internet Connection**
   - To install packages from PyPI

### Setup Steps

#### Quick Method (Recommended)
1. Copy the entire `alfhana_kitchen` folder to the new computer
2. Open the folder
3. Double-click `start.bat`
4. Wait for installation to complete (each step will be shown)
5. Open browser at `http://127.0.0.1:8000`

#### Manual Method
If the automatic file fails, follow these steps:

1. Open CMD or PowerShell in the project folder
2. Run the following commands:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python create_admin.py
python manage.py runserver
```

## Login Credentials

### Admin User
- **Username:** admin
- **Password:** admin123
- **Permissions:** Full

### Kitchen User
- **Username:** kitchen
- **Password:** kitchen123
- **Permissions:** Orders and menu management

### Driver User
- **Username:** driver1
- **Password:** driver123
- **Permissions:** Driver app only

## Common Issues and Solutions

### 1. Error: "python is not recognized"
**Solution:**
- Make sure Python is installed
- Reinstall Python and check "Add Python to PATH"
- Or add Python path manually to system variables

### 2. Error: "pip is not recognized"
**Solution:**
- Make sure Python is installed correctly
- Try using `python -m pip` instead of `pip`

### 3. Error: "No module named django"
**Solution:**
- Make sure Virtual Environment is activated: `venv\Scripts\activate`
- Reinstall packages: `pip install -r requirements.txt`

### 4. Error: "Access denied"
**Solution:**
- Run CMD as Administrator (Run as Administrator)
- Or make sure you have write permissions in the folder

### 5. Server not working
**Solution:**
- Make sure port 8000 is not in use
- Try using a different port: `python manage.py runserver 8080`

### 6. Pages not opening
**Solution:**
- Make sure server is running without errors
- Check that the URL is: `http://127.0.0.1:8000`
- Make sure no firewall is blocking the connection

## Data Transfer (Optional)

If you want to transfer data from the old computer:

1. Copy the `db.sqlite3` file from the old computer
2. Place it in the project folder on the new computer
3. Replace the old file (if exists)
4. No need to run migrations if database is transferred

## Important Notes

1. **Virtual Environment:** Created inside project for easy transfer
2. **Database:** SQLite doesn't need additional installation
3. **Static Files:** Auto-collected by `collectstatic`

## Support

If you encounter any issues:
1. Check all the steps mentioned above
2. Review `README.md` for more details
3. Make sure you're using Python 3.8 or later
