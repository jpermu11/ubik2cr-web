@echo off
echo ========================================
echo   CONFIGURACION URGENTE DE GIT
echo   Ubik2CR - Produccion
echo ========================================
echo.

REM Verificar si Git esta instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no esta instalado
    echo.
    echo INSTALACION URGENTE:
    echo 1. Descarga Git desde: https://git-scm.com/download/win
    echo 2. Instalalo marcando "Add Git to PATH"
    echo 3. Reinicia esta ventana
    echo.
    pause
    exit /b 1
)

echo Git encontrado!
git --version
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

echo [1/5] Inicializando repositorio Git...
if exist .git (
    echo Repositorio Git ya existe
    git remote -v
) else (
    git init
    echo Repositorio Git inicializado
)
echo.

echo [2/5] Configurando remoto de GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/jpermu11/ubik2cr-web.git
echo Remoto configurado: jpermu11/ubik2cr-web
echo.

echo [3/5] Configurando Git para este proyecto...
git config user.name "Ubik2CR Production" 2>nul
git config user.email "jpermu@gmail.com" 2>nul
echo Configuracion lista
echo.

echo [4/5] Agregando todos los archivos...
git add .
echo Archivos agregados
echo.

echo [5/5] Creando commit inicial...
git commit -m "Configuracion urgente - Recuperar conexion Git - Ubik2CR Produccion" 2>nul
if errorlevel 1 (
    echo Advertencia: No hay cambios nuevos para commit
) else (
    echo Commit creado exitosamente
)
echo.

echo ========================================
echo   CONFIGURACION COMPLETA
echo ========================================
echo.
echo IMPORTANTE: Ahora necesitas hacer PUSH:
echo.
echo 1. Si ya existe en GitHub:
echo    git pull origin main --allow-unrelated-histories
echo    git push -u origin main
echo.
echo 2. Si es la primera vez:
echo    git branch -M main
echo    git push -u origin main
echo.
echo ========================================
pause
