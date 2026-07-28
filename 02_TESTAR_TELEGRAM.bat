@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Testar Telegram

python configurar_telegram.py --check
if errorlevel 1 (
    echo.
    echo O teste falhou. Execute primeiro 01_CONFIGURAR_TELEGRAM.bat.
    pause
    exit /b 1
)

echo.
pause
