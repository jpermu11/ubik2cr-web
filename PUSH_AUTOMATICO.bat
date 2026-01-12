@echo off
cd /d "c:\Users\jperm\.cursor\flask-app"

REM Intentar usar Git si está disponible
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Git encontrado, haciendo push...
    git add .
    git commit -m "Aumentar tamano del logo"
    git push origin main
    echo Push completado!
    exit /b 0
)

REM Si Git no está disponible, intentar usar GitHub Desktop CLI
where gh >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo GitHub CLI encontrado, haciendo push...
    gh repo sync
    exit /b 0
)

echo Git no encontrado. Por favor usa GitHub Desktop manualmente.
echo Abre GitHub Desktop y haz commit y push de los cambios.
pause
