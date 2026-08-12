@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Configurar Telegram

if not exist "python\python.exe" (
    echo ERRO: python\python.exe nao encontrado.
    echo A pasta "python" faz parte do repositorio e nao deve ser apagada.
    pause
    exit /b 1
)

"python\python.exe" configurar_telegram.py
if errorlevel 1 (
    echo.
    echo A configuracao nao foi concluida.
    pause
    exit /b 1
)

echo.
echo Telegram configurado com sucesso.
pause
