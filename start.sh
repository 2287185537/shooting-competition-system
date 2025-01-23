#!/bin/bash

echo "[System] Shooting Competition Management System"
echo "============================================="

# Check conda
if ! command -v conda &> /dev/null; then
    echo "[Error] conda not found. Please install Anaconda or Miniconda"
    echo "Download: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Initialize conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate conda environment
echo "[Info] Activating conda environment (agent_learn)..."
if ! conda activate agent_learn; then
    echo "[Error] Cannot activate conda environment agent_learn"
    echo "Please create it using:"
    echo "conda create -n agent_learn python=3.8"
    exit 1
fi

# Uninstall potentially conflicting packages
echo "[Info] Removing old package versions..."
pip uninstall -y sqlalchemy flask-sqlalchemy

# Install dependencies in specific order
echo "[Info] Installing core dependencies..."
pip install "sqlalchemy==1.4.23"
pip install "flask==2.0.1"
pip install "flask-sqlalchemy==2.5.1"
pip install "pyodbc==4.0.39"

echo "[Info] Installing additional dependencies..."
pip install "flask-login==0.5.0"
pip install "werkzeug==2.0.1"
pip install "flask-migrate==3.1.0"
pip install "flask-wtf==0.15.1"
pip install "wtforms==2.3.3"
pip install "email-validator==1.1.3"
pip install "python-dotenv==0.19.0"
pip install "pytz==2021.1"
pip install "flask-talisman==0.8.1"
pip install "alembic==1.7.1"

# Initialize database
echo "[Info] Initializing database..."
echo "[Info] Using Windows Authentication"
echo "[Info] Server: DESKTOP-N0UKV4T"
if ! python init_db.py; then
    echo "[Error] Database initialization failed"
    echo "Please ensure:"
    echo "1. SQL Server is running"
    echo "2. Windows Authentication is enabled"
    echo "3. You have sufficient permissions"
    echo "4. SQL Server ODBC Driver 17 is installed"
    exit 1
fi

# Set environment variables
export FLASK_APP=run.py
export FLASK_ENV=development

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir logs
fi

# Start application
echo
echo "[Info] Starting application..."
echo "Default admin account:"
echo "Username: admin"
echo "Password: admin123"
echo
echo "Application will run at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "============================================="

# Run application
flask run

echo "Press Ctrl+C to exit..."