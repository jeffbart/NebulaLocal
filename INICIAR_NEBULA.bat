@echo off
setlocal
cd /d "%~dp0"
title Nebula Local FTP
chcp 65001 >nul
set PYTHONUTF8=1

if not exist ".env" (
    echo ERRO: arquivo .env nao encontrado.
    echo Execute primeiro 01_CONFIGURAR_TELEGRAM.bat.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: dependencias ainda nao foram instaladas.
    echo Execute primeiro 00_INSTALAR_DEPENDENCIAS.bat.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" setup_database.py
if errorlevel 1 goto :erro

echo.
echo Iniciando Nebula Local em ftp://127.0.0.1:2121
echo Pressione Ctrl+C para encerrar.
echo.
".venv\Scripts\python.exe" run_nebula.py
if errorlevel 1 goto :erro
exit /b 0

:erro
echo.
echo O Nebula foi encerrado com erro. Consulte nebula.log.
pause
exit /b 1
