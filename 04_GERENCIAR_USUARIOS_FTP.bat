@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Usuarios FTP

if not exist "python\python.exe" (
    echo ERRO: python\python.exe nao encontrado.
    echo A pasta "python" faz parte do repositorio e nao deve ser apagada.
    pause
    exit /b 1
)

"python\python.exe" accounts_manager.py

if errorlevel 1 (
    echo.
    echo Falha ao abrir o gerenciador de usuarios.
    pause
    exit /b 1
)
