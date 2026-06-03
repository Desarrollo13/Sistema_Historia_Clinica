@echo off
setlocal

set "BASE_DIR=%~dp0"
set "DB_FILE=%BASE_DIR%db.sqlite3"
set "BACKUP_DIR=%BASE_DIR%backups"

if not exist "%DB_FILE%" (
  echo [ERROR] No se encontro la base de datos en "%DB_FILE%".
  pause
  exit /b 1
)

if not exist "%BACKUP_DIR%" (
  mkdir "%BACKUP_DIR%"
  if errorlevel 1 (
    echo [ERROR] No se pudo crear la carpeta de backups.
    pause
    exit /b 1
  )
)

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format ''yyyy-MM-dd_HH-mm-ss''"') do set "STAMP=%%I"
set "TARGET=%BACKUP_DIR%\db_%STAMP%.sqlite3"

copy /Y "%DB_FILE%" "%TARGET%" >nul
if errorlevel 1 (
  echo [ERROR] No se pudo crear el backup.
  pause
  exit /b 1
)

echo Backup creado correctamente:
echo %TARGET%

endlocal
