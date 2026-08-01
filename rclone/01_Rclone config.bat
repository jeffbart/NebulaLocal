@echo off
setlocal
set "RCLONE_EXE=%~dp0rclone.exe"
set "RCLONE_CONFIG=%~dp0rclone.conf"

if not exist "%RCLONE_EXE%" (
    echo ERRO: rclone.exe nao encontrado na pasta deste arquivo BAT.
    pause
    exit /b 1
)

"%RCLONE_EXE%" config --config "%RCLONE_CONFIG%"
endlocal
