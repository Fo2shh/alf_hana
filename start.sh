#!/bin/bash

REPO_URL="https://github.com/Fo2shh/alf_hana.git"
TARGET_DIR="./alfhana_kitchen"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

if [ "$1" == "--clone-only" ]; then
    echo "Checking if project exists..."
    if [ ! -d "$TARGET_DIR" ]; then
        echo "Project not found, cloning from GitHub..."
        git clone "$REPO_URL" "$TARGET_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${RED}ERROR: Failed to clone repository${NC}"
            exit 1
        fi
        echo "Project cloned successfully"
    else
        echo "Project already exists"
    fi
    exit 0
fi

echo "========================================"
echo "    Alfhana Kitchen - Linux Setup"
echo "========================================"
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed${NC}"
    echo "Please install git and try again"
    exit 1
fi

echo "Git is available"

# Check if manage.py exists in current directory (Codespaces scenario)
if [ -f "manage.py" ]; then
    echo ""
    echo "Django project detected in current directory"
    echo "Using current directory"
    echo ""
else
    # Check if project directory exists
    if [ ! -d "$TARGET_DIR" ]; then
        echo ""
        echo "Project directory not found at $TARGET_DIR"
        echo "Downloading project from GitHub..."
        git clone "$REPO_URL" "$TARGET_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${RED}ERROR: Failed to clone repository${NC}"
            exit 1
        fi
        echo "Project downloaded successfully"
    else
        echo ""
        echo "Using existing project at $TARGET_DIR"
    fi

    echo ""
    cd "$TARGET_DIR"
fi

if [ "$1" == "--silent" ]; then
    echo "[1/7] Installing required packages..."
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    mkdir -p staticfiles
    python manage.py collectstatic --noinput
    python create_admin.py
    echo "[7/7] Starting server..."
    python manage.py runserver 0.0.0.0:8000
else
    echo "[1/7] Checking Virtual Environment..."
    if [ ! -d "venv" ]; then
        echo "venv not found, creating..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}ERROR: Failed to create Virtual Environment${NC}"
            exit 1
        fi
        echo "Virtual Environment created successfully"
    else
        echo "Virtual Environment exists"
    fi

    echo ""
    echo "[2/7] Activating Virtual Environment..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to activate Virtual Environment${NC}"
        exit 1
    fi
    echo "Virtual Environment activated successfully"
    echo ""

    echo "[3/7] Installing required packages..."
    pip install -r requirements.txt
    echo "Packages installed"
    echo ""

    echo "[4/7] Creating migrations..."
    python manage.py makemigrations
    echo ""

    echo "[5/7] Applying migrations to database..."
    python manage.py migrate
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to apply migrations${NC}"
        exit 1
    fi
    echo "Migrations applied successfully"
    echo ""

    echo "[6/7] Collecting static files..."
    mkdir -p staticfiles
    python manage.py collectstatic --noinput
    echo ""

    echo "[7/7] Creating users..."
    python create_admin.py
    echo ""

    echo "========================================"
    echo "     Setup completed successfully!"
    echo "========================================"
    echo ""
    echo "Login credentials:"
    echo "- Admin: admin / admin123"
    echo "- Kitchen: kitchen / kitchen123"
    echo "- Driver: driver1 / driver123"
    echo ""
    echo "Starting server..."
    echo "Open browser at: http://0.0.0.0:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "========================================"
    echo ""

    python manage.py runserver 0.0.0.0:8000
fi
