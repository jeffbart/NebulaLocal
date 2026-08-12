@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Criar SQLite

if not exist "python\python.exe" (
    echo ERRO: python\python.exe nao encontrado.
    echo A pasta "python" faz parte do repositorio e nao deve ser apagada.
    pause
    exit /b 1
)

"python\python.exe" setup_database.py
if errorlevel 1 (
    echo.
    echo Nao foi possivel criar o banco SQLite.
    pause
    exit /b 1
)

echo.
pause
