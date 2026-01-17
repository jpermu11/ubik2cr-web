@echo off
echo ========================================
echo   SOLUCIONAR ERROR DE POWERSHELL
echo ========================================
echo.
echo Este script habilita la ejecucion de scripts en PowerShell
echo para poder usar el entorno virtual.
echo.
echo Opciones:
echo   1. Permitir scripts solo para el usuario actual (RECOMENDADO)
echo   2. Cancelar
echo.
choice /C 12 /N /M "Elige una opcion: "
if errorlevel 2 goto cancelar
if errorlevel 1 goto permitir

:permitir
echo.
echo Habilitando ejecucion de scripts...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
if errorlevel 1 (
    echo ERROR: No se pudo cambiar la politica
    pause
    exit /b 1
)
echo.
echo ✅ Politica cambiada exitosamente!
echo.
echo Ahora puedes ejecutar los scripts .bat normalmente
echo.
pause
exit /b 0

:cancelar
echo.
echo Cancelado. Puedes usar EJECUTAR_CMD.bat en su lugar.
pause
