@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Instalar dependencias

where python >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao foi encontrado no PATH.
    echo Instale o Python 3.10 e marque "Add Python to PATH".
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 goto :erro
)

echo Instalando dependencias...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :erro
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo A instalacao normal falhou; tentando novamente pelos hosts oficiais do PyPI...
    ".venv\Scripts\python.exe" -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
    if errorlevel 1 goto :erro
)

echo.
echo Dependencias instaladas com sucesso.
pause
exit /b 0

:erro
echo.
echo Falha durante a instalacao.
pause
exit /b 1
