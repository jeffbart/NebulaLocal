@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Testar Telegram

if not exist "python\python.exe" (
    echo ERRO: python\python.exe nao encontrado.
    echo A pasta "python" faz parte do repositorio e nao deve ser apagada.
    pause
    exit /b 1
)

"python\python.exe" configurar_telegram.py --check
if errorlevel 1 (
    echo.
    echo O teste falhou. Execute primeiro 01_CONFIGURAR_TELEGRAM.bat.
    pause
    exit /b 1
)

echo.
pause
