@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Nebula Local - Verificar Acervo SQLite

if not exist "python\python.exe" (
    echo ERRO: python\python.exe nao encontrado.
    echo A pasta "python" faz parte do repositorio e nao deve ser apagada.
    pause
    exit /b 1
)
set "PYTHON_EXE=python\python.exe"

if not exist "logs" mkdir "logs"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "REPORT_TIMESTAMP=%%I"
set "REPORT_PATH=logs\relatorio_acervo_%REPORT_TIMESTAMP%.txt"

"%PYTHON_EXE%" verificar_acervo.py --saida "%REPORT_PATH%"
if errorlevel 1 (
    echo.
    echo Nao foi possivel verificar o acervo SQLite.
    pause
    exit /b 1
)

echo.
echo Verificacao concluida.
pause
