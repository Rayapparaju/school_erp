@echo off
title School ERP Setup
echo ============================================
echo  School ERP Management System - Setup
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)
echo [OK] Python detected

REM Create virtual environment
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
) else (
    echo [OK] Virtual environment exists
)

REM Activate and install
call venv\Scripts\activate.bat
echo [INFO] Installing dependencies...
pip install -r requirements.txt

REM Migrations
echo [INFO] Running migrations...
python manage.py makemigrations
python manage.py migrate

REM Static files
echo [INFO] Collecting static files...
python manage.py collectstatic --noinput

REM Create superuser
python manage.py createsuperuser

echo.
echo ============================================
echo  Setup Complete!
echo  Run: python manage.py runserver
echo  Then visit: http://127.0.0.1:8000/
echo ============================================
pause
