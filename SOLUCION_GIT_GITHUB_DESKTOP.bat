@echo off
echo ========================================
echo   SOLUCION: Usar GitHub Desktop
echo   Ubik2CR - Produccion
echo ========================================
echo.

REM Verificar si GitHub Desktop esta instalado
if exist "%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe" (
    echo ✅ GitHub Desktop encontrado!
    echo.
    echo OPCION 1: USAR GITHUB DESKTOP (RECOMENDADO)
    echo ========================================
    echo.
    echo 1. Abre GitHub Desktop
    echo 2. File → Add Local Repository
    echo 3. Selecciona esta carpeta:
    echo    %CD%
    echo.
    echo 4. Si dice "This directory does not appear to be a Git repository":
    echo    - Haz clic en "Create a Repository"
    echo    - Name: ubik2cr-web
    echo    - Haz clic en "Create Repository"
    echo.
    echo 5. Veras todos tus archivos en "Changes"
    echo 6. Abajo, en "Summary", escribe: "Configuracion urgente - Ubik2CR Produccion"
    echo 7. Haz clic en "Commit to main"
    echo 8. Arriba, haz clic en "Publish branch" o "Push origin"
    echo 9. Si te pide conectar, usa: jpermu11/ubik2cr-web
    echo.
    echo ========================================
    echo.
    echo ¿Quieres abrir GitHub Desktop ahora?
    echo (Se abrira automaticamente)
    echo.
    pause
    start "" "%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe"
    echo.
    echo GitHub Desktop abierto. Sigue los pasos arriba.
    echo.
) else (
    echo ❌ GitHub Desktop NO encontrado
    echo.
    echo OPCION 2: INSTALAR GIT FOR WINDOWS
    echo ========================================
    echo.
    echo 1. Descarga Git: https://git-scm.com/download/win
    echo 2. Instalalo marcando "Add Git to PATH"
    echo 3. Reinicia esta ventana
    echo 4. Ejecuta: setup_git_urgente.bat
    echo.
)

echo ========================================
pause
