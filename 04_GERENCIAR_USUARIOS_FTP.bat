@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Usuarios FTP

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" accounts_manager.py
) else (
    python accounts_manager.py
)

if errorlevel 1 (
    echo.
    echo Falha ao abrir o gerenciador de usuarios.
    pause
    exit /b 1
)
