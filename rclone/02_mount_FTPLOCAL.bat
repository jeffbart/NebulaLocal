@echo off
setlocal
title Rclone - FTPLOCAL na unidade S
color 2F

set "SCRIPT_DIR=%~dp0"
set "RCLONE_EXE=%SCRIPT_DIR%rclone.exe"
set "RCLONE_CONFIG=%SCRIPT_DIR%rclone.conf"
set "CACHE_ROOT=%LOCALAPPDATA%\NebulaLocal\rclone-cache"
set "MOUNT_DRIVE=S:"

if not exist "%RCLONE_EXE%" (
    echo ERRO: rclone.exe nao encontrado em:
    echo %RCLONE_EXE%
    echo.
    echo Coloque o rclone.exe na mesma pasta deste arquivo BAT.
    pause
    exit /b 1
)

if not exist "%RCLONE_CONFIG%" (
    echo ERRO: configuracao nao encontrada em:
    echo %RCLONE_CONFIG%
    echo.
    echo Execute primeiro 01_Rclone config.bat.
    pause
    exit /b 1
)

"%RCLONE_EXE%" listremotes --config "%RCLONE_CONFIG%" | findstr /b /x /c:"FTPLOCAL:" >nul
if errorlevel 1 (
    echo ERRO: o remoto FTPLOCAL nao existe em rclone.conf.
    echo Execute 01_Rclone config.bat e crie um remoto chamado FTPLOCAL.
    pause
    exit /b 1
)

if exist "%MOUNT_DRIVE%\" (
    echo ERRO: a unidade %MOUNT_DRIVE% ja esta em uso.
    echo Edite MOUNT_DRIVE neste arquivo para escolher outra letra.
    pause
    exit /b 1
)

if not exist "%CACHE_ROOT%\vfs" mkdir "%CACHE_ROOT%\vfs"
if not exist "%CACHE_ROOT%\logs" mkdir "%CACHE_ROOT%\logs"

echo ============================================================
echo  Montando FTPLOCAL na unidade %MOUNT_DRIVE%
echo ============================================================
echo.
echo Executavel: %RCLONE_EXE%
echo Cache VFS:  %CACHE_ROOT%\vfs
echo Log:        %CACHE_ROOT%\logs\FTPLOCAL.log
echo.
echo Mantenha esta janela aberta.
echo Para desmontar, pressione Ctrl+C.
echo.

"%RCLONE_EXE%" mount FTPLOCAL: %MOUNT_DRIVE% ^
    --config "%RCLONE_CONFIG%" ^
    --volname FTPLOCAL ^
    --network-mode ^
    --vfs-cache-mode full ^
    --cache-dir "%CACHE_ROOT%\vfs" ^
    --vfs-write-back 10s ^
    --vfs-read-chunk-size 32M ^
    --vfs-read-chunk-size-limit 512M ^
    --vfs-read-ahead 128M ^
    --buffer-size 32M ^
    --vfs-cache-max-age 168h ^
    --vfs-cache-max-size 100G ^
    --vfs-cache-poll-interval 1m ^
    --dir-cache-time 24h ^
    --poll-interval 0 ^
    --ftp-concurrency 2 ^
    --ftp-idle-timeout 1m ^
    --contimeout 15s ^
    --timeout 45s ^
    --low-level-retries 3 ^
    --ftp-disable-tls13 ^
    --log-file "%CACHE_ROOT%\logs\FTPLOCAL.log" ^
    --log-level INFO ^
    --stats 10s ^
    --stats-one-line ^
    --stats-log-level NOTICE

echo.
echo A unidade %MOUNT_DRIVE% foi desmontada.
pause
endlocal
