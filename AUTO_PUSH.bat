@echo off
chcp 65001 >nul
REM ========================================
REM   AUTO-PUSH AUTOMATICO
REM   Sube cambios a GitHub y Render.com
REM ========================================

cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo   AUTO-PUSH: Subiendo cambios a producción
echo ═══════════════════════════════════════════════════════════
echo.

REM Buscar Git en diferentes ubicaciones
set "GIT_CMD="

REM Intentar Git desde PATH
git --version >nul 2>&1
if not errorlevel 1 (
    set "GIT_CMD=git"
    goto :git_found
)

REM Intentar Git desde GitHub Desktop
set "GIT_DESKTOP=C:\Users\jperm\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"
if exist "%GIT_DESKTOP%" (
    set "GIT_CMD=%GIT_DESKTOP%"
    goto :git_found
)

REM Buscar cualquier versión de GitHub Desktop
for /d %%i in ("C:\Users\jperm\AppData\Local\GitHubDesktop\app-*") do (
    if exist "%%i\resources\app\git\cmd\git.exe" (
        set "GIT_CMD=%%i\resources\app\git\cmd\git.exe"
        goto :git_found
    )
)

REM Si no se encuentra, mostrar error
echo ❌ ERROR: Git no encontrado
echo.
echo Git debería estar con GitHub Desktop, pero no se encontró.
echo.
pause
exit /b 1

:git_found
echo ✅ Git encontrado
echo.

REM Agregar todos los cambios
echo [1/3] Agregando cambios...
"%GIT_CMD%" add .
if errorlevel 1 (
    echo ❌ ERROR: No se pudieron agregar los cambios
    pause
    exit /b 1
)
echo ✅ Cambios agregados
echo.

REM Crear commit automático con fecha/hora
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set fecha=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%
set hora=%datetime:~8,2%:%datetime:~10,2%

echo [2/3] Guardando cambios...
"%GIT_CMD%" commit -m "Auto-push: %fecha% %hora%" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No hay cambios nuevos para guardar
    echo.
    echo (Esto es normal si ya guardaste todo antes)
    echo.
) else (
    echo ✅ Cambios guardados (commit creado)
    echo.
)

REM Hacer push a GitHub
echo [3/3] Subiendo a GitHub...
"%GIT_CMD%" push origin main
if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se pudo hacer push
    echo.
    echo Posibles causas:
    echo - No hay conexión a internet
    echo - Credenciales de Git no configuradas
    echo - Repositorio remoto no configurado
    echo.
    echo Para configurar Git:
    echo   git config --global user.name "Tu Nombre"
    echo   git config --global user.email "tu@email.com"
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Push completado exitosamente
echo.
echo ═══════════════════════════════════════════════════════════
echo   DESPLIEGUE EN PROGRESO
echo ═══════════════════════════════════════════════════════════
echo.
echo Render.com está desplegando automáticamente...
echo.
echo 1. Ve a: https://render.com
echo 2. Dashboard → ubik2cr-web
echo 3. Revisa el estado del deploy (debe estar en verde)
echo.
echo ⏱️  Tiempo estimado: 2-5 minutos
echo.
echo ⚠️  IMPORTANTE: Verifica que el deploy se completó correctamente
echo.
pause
