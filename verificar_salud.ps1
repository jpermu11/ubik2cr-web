# ========================================
#   VERIFICACION DE SALUD - Ubik2CR
#   Produccion - Ejecutar diariamente
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICACION DE SALUD - Ubik2CR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()

# 1. Verificar que Git está activo
Write-Host "[1/5] Verificando Git..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "  ✅ Git está activo" -ForegroundColor Green
    $gitStatus = git status --short 2>$null
    if ($gitStatus) {
        Write-Host "  ⚠️  Hay cambios sin commit:" -ForegroundColor Yellow
        Write-Host $gitStatus
        $errors += "Hay cambios sin commit"
    } else {
        Write-Host "  ✅ No hay cambios pendientes" -ForegroundColor Green
    }
} else {
    Write-Host "  ❌ ERROR: Git NO está activo!" -ForegroundColor Red
    $errors += "Git no está activo - Ejecutar setup_git_urgente.bat"
}

Write-Host ""

# 2. Verificar conexión a GitHub
Write-Host "[2/5] Verificando conexión a GitHub..." -ForegroundColor Yellow
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "  ✅ Remoto configurado: $remote" -ForegroundColor Green
    
    # Intentar fetch (sin cambios, solo verificar conexión)
    $fetchResult = git fetch --dry-run 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Conexión a GitHub funciona" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Problema de conexión a GitHub" -ForegroundColor Yellow
        $errors += "Problema de conexión a GitHub"
    }
} else {
    Write-Host "  ❌ ERROR: No hay remoto configurado" -ForegroundColor Red
    $errors += "No hay remoto Git configurado"
}

Write-Host ""

# 3. Verificar salud de la aplicación en Render
Write-Host "[3/5] Verificando salud de la aplicación..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://ubik2cr.com/health" -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ Aplicación respondiendo correctamente" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Aplicación respondió con código: $($response.StatusCode)" -ForegroundColor Yellow
        $errors += "Aplicación respondió con código $($response.StatusCode)"
    }
} catch {
    Write-Host "  ❌ ERROR: No se pudo conectar a la aplicación" -ForegroundColor Red
    Write-Host "    Mensaje: $($_.Exception.Message)" -ForegroundColor Red
    $errors += "Aplicación no responde"
}

Write-Host ""

# 4. Verificar archivos críticos
Write-Host "[4/5] Verificando archivos críticos..." -ForegroundColor Yellow
$criticalFiles = @("main.py", "models.py", "requirements.txt", ".gitignore")
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file existe" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ERROR: $file NO existe!" -ForegroundColor Red
        $errors += "$file no existe"
    }
}

Write-Host ""

# 5. Verificar backup reciente
Write-Host "[5/5] Verificando backup reciente..." -ForegroundColor Yellow
$backupLog = "backup_errors.log"
if (Test-Path $backupLog) {
    $lastError = Get-Content $backupLog -Tail 1 -ErrorAction SilentlyContinue
    if ($lastError -like "*ERROR*") {
        Write-Host "  ⚠️  Último backup tuvo errores:" -ForegroundColor Yellow
        Write-Host "    $lastError" -ForegroundColor Yellow
        $errors += "Backup tuvo errores recientes"
    } else {
        Write-Host "  ✅ No hay errores de backup recientes" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠️  No se encontró log de backup (puede ser normal si no se ejecutó aún)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Resumen
if ($errors.Count -eq 0) {
    Write-Host "✅ TODO OK - Sistema funcionando correctamente" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ SE ENCONTRARON $($errors.Count) PROBLEMA(S):" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "⚠️  ACCIÓN REQUERIDA: Resolver los problemas antes de continuar" -ForegroundColor Yellow
    exit 1
}
