@echo off
setlocal
cd /d "%~dp0"
title Nebula Local - Descobrir CHAT_ID

echo ============================================================
echo Antes de continuar:
echo 1. Adicione o bot como administrador do canal.
echo 2. Publique uma mensagem NOVA no canal.
echo 3. Mantenha o Nebula desligado.
echo ============================================================
echo.
pause

if not exist "python\python.exe" (
    echo ERRO: python\python.exe nao encontrado.
    echo A pasta "python" faz parte do repositorio e nao deve ser apagada.
    pause
    exit /b 1
)

"python\python.exe" configurar_telegram.py --discover-chat
if errorlevel 1 (
    echo.
    echo O canal ainda nao foi encontrado. Confira as instrucoes acima.
    pause
    exit /b 1
)

echo.
echo CHAT_ID encontrado e salvo no arquivo .env.
pause
