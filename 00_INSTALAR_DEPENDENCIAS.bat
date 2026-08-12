@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Instalar dependencias

if not exist "python\python.exe" (
    echo ERRO: python\python.exe nao encontrado.
    echo A pasta "python" faz parte do repositorio e nao deve ser apagada.
    pause
    exit /b 1
)

echo Verificando dependencias no Python portatil incluido no projeto...
"python\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo A instalacao normal falhou; tentando novamente pelos hosts oficiais do PyPI...
    "python\python.exe" -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
    if errorlevel 1 goto :erro
)

echo.
echo Dependencias prontas. O projeto ja inclui um Python 3.11 proprio; nao e necessario instalar Python no sistema.
pause
exit /b 0

:erro
echo.
echo Falha durante a instalacao.
pause
exit /b 1
