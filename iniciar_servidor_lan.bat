@echo off
setlocal
title Servidor LAN - Historia Clinica

set "BASE_DIR=%~dp0"
set "PYTHON_EXE=%BASE_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] No se encontro el entorno virtual en "%PYTHON_EXE%".
  pause
  exit /b 1
)

if not exist "%BASE_DIR%manage.py" (
  echo [ERROR] No se encontro manage.py en "%BASE_DIR%".
  pause
  exit /b 1
)

rem Configuracion LAN y datos del consultorio.
rem Ajustar estos valores antes de usar en la PC servidor.
set "CLINICA_SECRET_KEY=cambiar-esta-clave-local"
set "CLINICA_DEBUG=False"
set "CLINICA_ALLOWED_HOSTS=127.0.0.1,localhost,DESKTOP-I9N9O2K,192.168.1.105"
set "CLINICA_CONSULTORIO_NOMBRE=Consultorio Medico"
set "CLINICA_CONSULTORIO_DIRECCION=Direccion no configurada"
set "CLINICA_CONSULTORIO_TELEFONO=Tel: no configurado"
set "CLINICA_CONSULTORIO_EMAIL=consultas@clinica.local"
set "CLINICA_CONSULTORIO_CIUDAD=Ciudad no configurada"

echo.
echo ================================================
echo   Sistema de Historia Clinica - Servidor LAN
echo ================================================
echo.
echo Reuniendo archivos estaticos...
call "%PYTHON_EXE%" "%BASE_DIR%manage.py" collectstatic --noinput
if errorlevel 1 (
  echo.
  echo [ERROR] Fallo collectstatic.
  pause
  exit /b 1
)

echo.
echo Aplicando migraciones...
call "%PYTHON_EXE%" "%BASE_DIR%manage.py" migrate
if errorlevel 1 (
  echo.
  echo [ERROR] Fallaron las migraciones.
  pause
  exit /b 1
)

echo.
echo Iniciando servidor en 0.0.0.0:8000 ...
echo Acceso local:  http://127.0.0.1:8000/
echo Acceso por red: http://192.168.1.105:8000/
echo Deja esta ventana abierta mientras el sistema este en uso.
echo.
call "%PYTHON_EXE%" "%BASE_DIR%manage.py" runserver 0.0.0.0:8000 --insecure

if errorlevel 1 (
  echo.
  echo [ERROR] El servidor se detuvo con un error.
  pause
  exit /b 1
)

echo.
echo El servidor se cerro.
pause

endlocal
