@echo off
chcp 65001
cls

echo [System] Shooting Competition Management System
echo =============================================

:: Check conda environment
where conda > nul 2>&1
if errorlevel 1 (
    echo [Error] Conda not found. Please install Anaconda or Miniconda
    pause
    exit
)

:: Activate conda environment
echo [Info] Activating conda environment (agent_learn)...
call conda activate agent_learn
if errorlevel 1 (
    echo [Error] Cannot activate conda environment agent_learn
    echo Please create it using: conda create -n agent_learn python=3.8
    pause
    exit
)

:: Uninstall potentially conflicting packages
echo [Info] Removing old package versions...
pip uninstall -y sqlalchemy flask-sqlalchemy

:: Install dependencies in specific order
echo [Info] Installing core dependencies...
pip install "sqlalchemy==1.4.23"
pip install "flask==2.0.1"
pip install "flask-sqlalchemy==2.5.1"
pip install "pyodbc==4.0.39"

echo [Info] Installing additional dependencies...
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

:: Initialize database
echo [Info] Initializing database...
echo [Info] Using Windows Authentication
echo [Info] Server: DESKTOP-N0UKV4T
python init_db.py
if errorlevel 1 (
    echo [Error] Database initialization failed
    echo Please ensure:
    echo 1. SQL Server is running
    echo 2. Windows Authentication is enabled
    echo 3. You have sufficient permissions
    echo 4. SQL Server ODBC Driver 17 is installed
    pause
    exit
)

:: Set environment variables
set FLASK_APP=run.py
set FLASK_ENV=development

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Start application
echo.
echo [Info] Starting application...
echo Default admin account:
echo Username: admin
echo Password: admin123
echo.
echo Application will run at http://localhost:5000
echo Press Ctrl+C to stop the server
echo =============================================

:: Run the application
flask run

:: Prompt user
echo.
echo Press any key to exit...
pause