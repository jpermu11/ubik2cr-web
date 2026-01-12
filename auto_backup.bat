@echo off
REM ========================================
REM   AUTO-BACKUP AUTOMATICO
REM   Ubik2CR - Produccion
REM   Ejecutar cada hora o configurar en Task Scheduler
REM ========================================

cd /d "%~dp0"

echo [%date% %time%] Iniciando backup automatico...

REM 1. Commit automatico de cambios
git add . 2>nul
git commit -m "Auto-backup: %date% %time%" 2>nul
if errorlevel 1 (
    echo No hay cambios nuevos
) else (
    echo Cambios commitados
)

REM 2. Push a GitHub (backup remoto)
git push origin main 2>nul
if errorlevel 1 (
    echo ERROR: No se pudo hacer push. Verificar conexion.
    echo Guardar log de error...
    echo ERROR: Push fallido %date% %time% >> backup_errors.log
) else (
    echo Backup remoto completado en GitHub
)

REM 3. Crear copia local de seguridad (opcional)
if not exist "..\backup_ubik2cr" mkdir "..\backup_ubik2cr"
xcopy /E /I /Y main.py "..\backup_ubik2cr\" >nul 2>&1
xcopy /E /I /Y models.py "..\backup_ubik2cr\" >nul 2>&1
xcopy /E /I /Y templates "..\backup_ubik2cr\templates\" >nul 2>&1

echo [%date% %time%] Backup completado
echo.
