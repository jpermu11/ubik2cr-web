@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo   VERIFICACIÓN AUTOMÁTICA - Ubik2CR Producción
echo ═══════════════════════════════════════════════════════════
echo.
echo Verificando configuración para miles de usuarios...
echo.
cd /d "%~dp0"

set errores=0

REM ========================================
REM 1. VERIFICAR ARCHIVOS CRÍTICOS
REM ========================================
echo [1/8] Verificando archivos críticos...
if exist "main.py" (
    echo   ✅ main.py existe
) else (
    echo   ❌ ERROR: main.py NO existe
    set /a errores+=1
)
if exist "models.py" (
    echo   ✅ models.py existe
) else (
    echo   ❌ ERROR: models.py NO existe
    set /a errores+=1
)
if exist "requirements.txt" (
    echo   ✅ requirements.txt existe
) else (
    echo   ❌ ERROR: requirements.txt NO existe
    set /a errores+=1
)
if exist "render.yaml" (
    echo   ✅ render.yaml existe
) else (
    echo   ❌ ERROR: render.yaml NO existe
    set /a errores+=1
)
echo.

REM ========================================
REM 2. VERIFICAR GUNICORN
REM ========================================
echo [2/8] Verificando Gunicorn (servidor producción)...
findstr /C:"gunicorn" requirements.txt >nul 2>&1
if errorlevel 1 (
    echo   ❌ ERROR: Gunicorn NO está en requirements.txt
    set /a errores+=1
) else (
    echo   ✅ Gunicorn configurado en requirements.txt
)
findstr /C:"gunicorn" render.yaml >nul 2>&1
if errorlevel 1 (
    echo   ❌ ERROR: Gunicorn NO está en render.yaml
    set /a errores+=1
) else (
    echo   ✅ Gunicorn configurado en render.yaml
)
echo.

REM ========================================
REM 3. VERIFICAR SESSION_SECRET
REM ========================================
echo [3/8] Verificando SESSION_SECRET...
findstr /C:"SESSION_SECRET" render.yaml >nul 2>&1
if errorlevel 1 (
    echo   ❌ ERROR: SESSION_SECRET NO está en render.yaml
    set /a errores+=1
) else (
    echo   ✅ SESSION_SECRET configurado en render.yaml
    findstr /C:"generateValue: true" render.yaml >nul 2>&1
    if errorlevel 1 (
        echo   ⚠️  ADVERTENCIA: SESSION_SECRET no se genera automáticamente
    ) else (
        echo   ✅ SESSION_SECRET se genera automáticamente en Render
    )
)
echo.

REM ========================================
REM 4. VERIFICAR HEALTH CHECKS
REM ========================================
echo [4/8] Verificando Health Checks...
findstr /C:"/health" render.yaml >nul 2>&1
if errorlevel 1 (
    echo   ❌ ERROR: Health check NO está configurado en render.yaml
    set /a errores+=1
) else (
    echo   ✅ Health check configurado en render.yaml
)
findstr /C:"@app.route.*health" main.py >nul 2>&1
if errorlevel 1 (
    echo   ❌ ERROR: Health check NO está implementado en main.py
    set /a errores+=1
) else (
    echo   ✅ Health check implementado en main.py
)
echo.

REM ========================================
REM 5. VERIFICAR POOL DE CONEXIONES
REM ========================================
echo [5/8] Verificando Pool de Conexiones...
findstr /C:"pool_size" main.py >nul 2>&1
if errorlevel 1 (
    echo   ❌ ERROR: Pool de conexiones NO está configurado
    set /a errores+=1
) else (
    echo   ✅ Pool de conexiones configurado
)
echo.

REM ========================================
REM 6. VERIFICAR ERROR HANDLERS
REM ========================================
echo [6/8] Verificando Error Handlers...
findstr /C:"@app.errorhandler" main.py >nul 2>&1
if errorlevel 1 (
    echo   ❌ ERROR: Error handlers NO están implementados
    set /a errores+=1
) else (
    echo   ✅ Error handlers implementados
)
if exist "templates\404.html" (
    echo   ✅ Template 404.html existe
) else (
    echo   ⚠️  Template 404.html NO existe (opcional)
)
if exist "templates\500.html" (
    echo   ✅ Template 500.html existe
) else (
    echo   ⚠️  Template 500.html NO existe (opcional)
)
echo.

REM ========================================
REM 7. VERIFICAR DEBUG MODE
REM ========================================
echo [7/8] Verificando Debug Mode...
findstr /C:"debug=False" main.py >nul 2>&1
if errorlevel 1 (
    findstr /C:"debug=True" main.py >nul 2>&1
    if not errorlevel 1 (
        echo   ⚠️  ADVERTENCIA: Debug=True encontrado (debe ser False en producción)
    ) else (
        echo   ✅ Debug mode no está en True (correcto)
    )
) else (
    echo   ✅ Debug=False configurado (correcto para producción)
)
echo.

REM ========================================
REM 8. VERIFICAR POSTGRESQL
REM ========================================
echo [8/8] Verificando PostgreSQL...
findstr /C:"psycopg2" requirements.txt >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  ADVERTENCIA: psycopg2 no está en requirements.txt (necesario para PostgreSQL)
) else (
    echo   ✅ psycopg2 configurado (PostgreSQL)
)
echo.

REM ========================================
REM RESUMEN
REM ========================================
echo ═══════════════════════════════════════════════════════════
echo   RESUMEN DE VERIFICACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
if %errores% EQU 0 (
    echo ✅ TODO ESTÁ BIEN CONFIGURADO
    echo.
    echo Tu código está listo para producción.
    echo.
    echo ⚠️  IMPORTANTE: Ahora necesitas verificar en Render.com:
    echo.
    echo 1. Ve a: https://render.com
    echo 2. Dashboard → ubik2cr-web → Settings → Notifications
    echo 3. Activa alertas por email
    echo.
    echo 4. Render.com → ubik2cr-db-oregon → Settings → Backups
    echo 5. Verifica que Auto-Backup esté activado
    echo.
    echo Ver instrucciones detalladas en: VERIFICAR_RENDER.md
) else (
    echo ❌ SE ENCONTRARON %errores% ERRORES
    echo.
    echo Revisa los errores arriba y corrígelos.
)
echo.
pause
