@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Criar SQLite

python setup_database.py
if errorlevel 1 (
    echo.
    echo Nao foi possivel criar o banco SQLite.
    pause
    exit /b 1
)

echo.
pause
