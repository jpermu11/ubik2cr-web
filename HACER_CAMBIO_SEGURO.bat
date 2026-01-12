@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo   ASISTENTE: HACER CAMBIOS SEGUROS
echo   Protege tus datos de usuarios
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script te guiará para hacer cambios SIN perder datos.
echo.
echo IMPORTANTE: Tus datos están en Render.com y están SEGUROS.
echo Modificar código aquí NO afecta los datos de usuarios.
echo.
pause
echo.
echo ═══════════════════════════════════════════════════════════
echo   PASO 1: BACKUP ANTES DE CAMBIAR
echo ═══════════════════════════════════════════════════════════
echo.
echo ¿Quieres hacer un backup ahora? (S/N)
set /p hacer_backup="> "
if /i "%hacer_backup%"=="S" (
    echo.
    echo Haciendo backup...
    call auto_backup.bat
    echo.
    echo ✅ Backup completado
) else (
    echo.
    echo ⚠️  Continuando sin backup (ya tienes backups automáticos)
)
echo.
pause
echo.
echo ═══════════════════════════════════════════════════════════
echo   PASO 2: VERIFICAR CAMBIOS
echo ═══════════════════════════════════════════════════════════
echo.
echo ¿Modificaste models.py? (S/N)
echo (Si solo modificaste main.py o templates, responde N)
set /p modifico_models="> "
echo.
if /i "%modifico_models%"=="S" (
    echo ═══════════════════════════════════════════════════════════
    echo   CREAR MIGRACIÓN
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Escribe una descripción de los cambios:
    set /p descripcion="> "
    echo.
    echo Creando migración...
    flask db migrate -m "%descripcion%"
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: No se pudo crear la migración
        echo.
        echo Posibles causas:
        echo - No hay cambios detectados
        echo - Error de sintaxis en models.py
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ Migración creada
    echo.
    pause
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo   APLICAR MIGRACIÓN LOCALMENTE
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo Aplicando migración a tu base de datos local...
    flask db upgrade
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: La migración falló
        echo.
        echo Revisa los errores arriba y corrige el problema.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ Migración aplicada localmente
    echo.
) else (
    echo.
    echo ✅ No necesitas crear migración (no modificaste models.py)
)
echo.
pause
echo.
echo ═══════════════════════════════════════════════════════════
echo   PASO 3: PROBAR LOCALMENTE
echo ═══════════════════════════════════════════════════════════
echo.
echo ⚠️  IMPORTANTE: Debes probar tu aplicación ANTES de desplegar
echo.
echo 1. Abre OTRA ventana de terminal
echo 2. Ejecuta: EJECUTAR.bat
echo 3. Prueba TODO lo que modificaste
echo 4. Verifica que funciona correctamente
echo.
echo ¿Ya probaste y todo funciona? (S/N)
set /p probo="> "
if /i NOT "%probo%"=="S" (
    echo.
    echo ⚠️  Es MUY IMPORTANTE probar antes de desplegar
    echo.
    echo Presiona cualquier tecla cuando hayas probado...
    pause
)
echo.
echo ═══════════════════════════════════════════════════════════
echo   PASO 4: DESPLEGAR A PRODUCCIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo Para desplegar, necesitas hacer commit y push a GitHub.
echo.
echo ¿Tienes Git instalado y configurado? (S/N)
set /p tiene_git="> "
if /i NOT "%tiene_git%"=="S" (
    echo.
    echo ❌ Necesitas Git para desplegar
    echo.
    echo Opciones:
    echo 1. Instalar Git: https://git-scm.com/download/win
    echo 2. Usar GitHub Desktop (más fácil)
    echo.
    echo Para ahora, puedes guardar los cambios manualmente.
    echo Cuando tengas Git, haz commit y push.
    echo.
    pause
    exit /b 0
)
echo.
echo ¿Quieres hacer commit y push ahora? (S/N)
set /p hacer_commit="> "
if /i "%hacer_commit%"=="S" (
    echo.
    echo Escribe un mensaje para el commit:
    echo (Ejemplo: "Agregué página de contacto")
    set /p commit_msg="> "
    echo.
    echo Haciendo commit...
    git add .
    git commit -m "%commit_msg%"
    if errorlevel 1 (
        echo.
        echo ⚠️  No se pudo hacer commit (puede que no haya cambios)
    ) else (
        echo ✅ Commit realizado
        echo.
        echo Haciendo push a GitHub...
        git push origin main
        if errorlevel 1 (
            echo.
            echo ❌ ERROR: No se pudo hacer push
            echo.
            echo Verifica tu conexión a Internet y configuración de Git
        ) else (
            echo.
            echo ✅ Push completado
            echo.
            echo ═══════════════════════════════════════════════════════════
            echo   DESPLIEGUE EN PROGRESO
            echo ═══════════════════════════════════════════════════════════
            echo.
            echo Render.com está desplegando automáticamente...
            echo.
            echo 1. Ve a https://render.com
            echo 2. Dashboard → ubik2cr-web
            echo 3. Revisa el estado del deploy (debe estar en verde)
            echo.
            echo Tiempo estimado: 2-5 minutos
            echo.
            echo ⚠️  IMPORTANTE: Verifica que el deploy se completó correctamente
        )
    )
) else (
    echo.
    echo ✅ Continuando sin commit (puedes hacerlo después)
    echo.
    echo Para desplegar más tarde:
    echo   git add .
    echo   git commit -m "Descripción de cambios"
    echo   git push origin main
)
echo.
echo ═══════════════════════════════════════════════════════════
echo   RESUMEN
echo ═══════════════════════════════════════════════════════════
echo.
echo ✅ Proceso completado
echo.
echo RECUERDA:
echo - Tus datos de usuarios están SEGUROS en Render.com
echo - Las migraciones NO borran datos
echo - Puedes revertir cualquier cambio si es necesario
echo - Siempre prueba localmente antes de desplegar
echo.
echo Para más información, lee: CAMBIOS_SEGUROS.md
echo.
pause
