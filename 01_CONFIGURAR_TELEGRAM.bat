@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Configurar Telegram

where python >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao foi encontrado no PATH.
    echo Instale o Python 3.10 e marque "Add Python to PATH".
    pause
    exit /b 1
)

python configurar_telegram.py
if errorlevel 1 (
    echo.
    echo A configuracao nao foi concluida.
    pause
    exit /b 1
)

echo.
echo Telegram configurado com sucesso.
pause
