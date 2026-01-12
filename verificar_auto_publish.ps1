# ========================================
#   VERIFICACION AUTO-PUBLISH - Ubik2CR
#   Verifica que todo está configurado correctamente
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICACION AUTO-PUBLISH - Ubik2CR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()
$success = @()

# 1. Verificar que Git está configurado
Write-Host "[1/6] Verificando repositorio Git..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "  ✅ Repositorio Git existe" -ForegroundColor Green
    $success += "Repositorio Git configurado"
    
    # Verificar remoto
    $remote = git remote get-url origin 2>&1
    if ($LASTEXITCODE -eq 0 -and $remote -notlike "*error*") {
        Write-Host "  ✅ Remoto configurado: $remote" -ForegroundColor Green
        $success += "Remoto Git configurado: $remote"
        
        # Verificar que es el repositorio correcto
        if ($remote -like "*jpermu11/ubik2cr-web*" -or $remote -like "*github.com/jpermu11/ubik2cr-web*") {
            Write-Host "  ✅ Repositorio correcto: ubik2cr-web" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  ADVERTENCIA: Remoto no es ubik2cr-web" -ForegroundColor Yellow
            $warnings += "Remoto Git no es el repositorio esperado"
        }
    } else {
        Write-Host "  ❌ ERROR: No hay remoto configurado" -ForegroundColor Red
        $errors += "No hay remoto Git configurado - Ejecutar: git remote add origin https://github.com/jpermu11/ubik2cr-web.git"
    }
    
    # Verificar branch
    $branch = git branch --show-current 2>&1
    if ($LASTEXITCODE -eq 0 -and $branch) {
        Write-Host "  ✅ Rama actual: $branch" -ForegroundColor Green
        if ($branch -eq "main" -or $branch -eq "master") {
            Write-Host "  ✅ Rama correcta: $branch" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  ADVERTENCIA: Rama no es main/master" -ForegroundColor Yellow
            $warnings += "Rama actual es '$branch', se recomienda 'main'"
        }
    }
    
    # Verificar cambios sin commit
    $status = git status --short 2>&1
    if ($status) {
        Write-Host "  ⚠️  ADVERTENCIA: Hay cambios sin commit:" -ForegroundColor Yellow
        Write-Host $status
        $warnings += "Hay cambios sin commit - Hacer commit y push"
    } else {
        Write-Host "  ✅ No hay cambios pendientes" -ForegroundColor Green
        $success += "Todo está commiteado"
    }
    
} else {
    Write-Host "  ❌ ERROR: No hay repositorio Git configurado" -ForegroundColor Red
    $errors += "No hay repositorio Git - Necesitas configurar Git primero"
}

Write-Host ""

# 2. Verificar conexión a GitHub
Write-Host "[2/6] Verificando conexión a GitHub..." -ForegroundColor Yellow
if (Test-Path ".git") {
    try {
        $fetchResult = git ls-remote --heads origin 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Conexión a GitHub funciona" -ForegroundColor Green
            $success += "Conexión a GitHub OK"
        } else {
            Write-Host "  ❌ ERROR: No se puede conectar a GitHub" -ForegroundColor Red
            Write-Host "    Mensaje: $fetchResult" -ForegroundColor Red
            $errors += "Problema de conexión a GitHub - Verificar credenciales"
        }
    } catch {
        Write-Host "  ❌ ERROR: Error al verificar GitHub" -ForegroundColor Red
        $errors += "Error al verificar GitHub: $($_.Exception.Message)"
    }
} else {
    Write-Host "  ⚠️  No se puede verificar (Git no configurado)" -ForegroundColor Yellow
}

Write-Host ""

# 3. Verificar que los archivos están listos para push
Write-Host "[3/6] Verificando archivos críticos..." -ForegroundColor Yellow
$criticalFiles = @("main.py", "models.py", "requirements.txt", "render.yaml")
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file existe" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ERROR: $file NO existe" -ForegroundColor Red
        $errors += "$file no existe"
    }
}

Write-Host ""

# 4. Verificar configuración de Render (render.yaml)
Write-Host "[4/6] Verificando configuración de Render..." -ForegroundColor Yellow
if (Test-Path "render.yaml") {
    Write-Host "  ✅ render.yaml existe" -ForegroundColor Green
    $renderYaml = Get-Content "render.yaml" -Raw
    if ($renderYaml -like "*ubik2cr-web*") {
        Write-Host "  ✅ Nombre del servicio correcto: ubik2cr-web" -ForegroundColor Green
        $success += "Configuración Render correcta"
    } else {
        Write-Host "  ⚠️  ADVERTENCIA: Nombre del servicio no es ubik2cr-web" -ForegroundColor Yellow
        $warnings += "Verificar nombre del servicio en render.yaml"
    }
    
    if ($renderYaml -like "*buildCommand*") {
        Write-Host "  ✅ Build command configurado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  ADVERTENCIA: No hay build command en render.yaml" -ForegroundColor Yellow
        $warnings += "No hay build command configurado"
    }
    
    if ($renderYaml -like "*startCommand*") {
        Write-Host "  ✅ Start command configurado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  ADVERTENCIA: No hay start command en render.yaml" -ForegroundColor Yellow
        $warnings += "No hay start command configurado"
    }
} else {
    Write-Host "  ❌ ERROR: render.yaml no existe" -ForegroundColor Red
    $errors += "render.yaml no existe - Render puede no detectar cambios"
}

Write-Host ""

# 5. Verificar salud de la aplicación en producción
Write-Host "[5/6] Verificando aplicación en producción..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://ubik2cr.com/health" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ Aplicación respondiendo en producción" -ForegroundColor Green
        $success += "Aplicación en producción funcionando"
        
        $healthContent = $response.Content
        if ($healthContent -like '*"status":"ok"*') {
            Write-Host "  ✅ Health check responde correctamente" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Health check responde pero formato inusual" -ForegroundColor Yellow
            $warnings += "Verificar formato del health check"
        }
    } else {
        Write-Host "  ⚠️  Aplicación respondió con código: $($response.StatusCode)" -ForegroundColor Yellow
        $warnings += "Health check respondió con código $($response.StatusCode)"
    }
} catch {
    Write-Host "  ❌ ERROR: No se pudo conectar a la aplicación en producción" -ForegroundColor Red
    Write-Host "    URL: https://ubik2cr.com/health" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    $errors += "Aplicación no responde en producción - Verificar Render.com"
}

Write-Host ""

# 6. Verificar auto-backup configurado
Write-Host "[6/6] Verificando auto-backup..." -ForegroundColor Yellow
if (Test-Path "auto_backup.bat") {
    Write-Host "  ✅ Script de auto-backup existe" -ForegroundColor Green
    
    # Verificar si está en Task Scheduler (solo Windows)
    $taskName = "Ubik2CR_Auto_Backup"
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "  ✅ Auto-backup configurado en Task Scheduler" -ForegroundColor Green
        $success += "Auto-backup configurado"
        
        $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
        Write-Host "    Última ejecución: $($taskInfo.LastRunTime)" -ForegroundColor Gray
        Write-Host "    Próxima ejecución: $($taskInfo.NextRunTime)" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  ADVERTENCIA: Auto-backup NO está en Task Scheduler" -ForegroundColor Yellow
        $warnings += "Auto-backup no está programado - Configurar en Task Scheduler"
        Write-Host "    Instrucciones: Ver URGENTE_PASOS_INMEDIATOS.txt" -ForegroundColor Gray
    }
    
    # Verificar log de errores
    if (Test-Path "backup_errors.log") {
        $lastError = Get-Content "backup_errors.log" -Tail 1 -ErrorAction SilentlyContinue
        if ($lastError -like "*ERROR*") {
            Write-Host "  ⚠️  ADVERTENCIA: Último backup tuvo errores" -ForegroundColor Yellow
            Write-Host "    Ver: backup_errors.log" -ForegroundColor Gray
            $warnings += "Backup tuvo errores recientes"
        } else {
            Write-Host "  ✅ No hay errores de backup recientes" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  ⚠️  ADVERTENCIA: Script de auto-backup no existe" -ForegroundColor Yellow
    $warnings += "Auto-backup no configurado - Ejecutar auto_backup.bat manualmente"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mostrar éxito
if ($success.Count -gt 0) {
    Write-Host "✅ ÉXITOS ($($success.Count)):" -ForegroundColor Green
    foreach ($s in $success) {
        Write-Host "  ✅ $s" -ForegroundColor Green
    }
    Write-Host ""
}

# Mostrar advertencias
if ($warnings.Count -gt 0) {
    Write-Host "⚠️  ADVERTENCIAS ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($w in $warnings) {
        Write-Host "  ⚠️  $w" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Mostrar errores
if ($errors.Count -gt 0) {
    Write-Host "❌ ERRORES CRÍTICOS ($($errors.Count)):" -ForegroundColor Red
    foreach ($e in $errors) {
        Write-Host "  ❌ $e" -ForegroundColor Red
    }
    Write-Host ""
}

# Resumen final
Write-Host "========================================" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✅ TODO PERFECTO - Auto-publish configurado correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "FLUJO FUNCIONANDO:" -ForegroundColor Green
    Write-Host "  1. Cambios locales →" -ForegroundColor Gray
    Write-Host "  2. Commit a Git →" -ForegroundColor Gray
    Write-Host "  3. Push a GitHub →" -ForegroundColor Gray
    Write-Host "  4. Render detecta automáticamente →" -ForegroundColor Gray
    Write-Host "  5. Auto-deploy en producción ✅" -ForegroundColor Green
    exit 0
} elseif ($errors.Count -eq 0) {
    Write-Host "⚠️  FUNCIONAL pero hay advertencias - Revisar arriba" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "El auto-publish debería funcionar, pero hay mejoras recomendadas." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "❌ PROBLEMAS CRÍTICOS - Auto-publish NO funcionará correctamente" -ForegroundColor Red
    Write-Host ""
    Write-Host "ACCIÓN REQUERIDA: Resolver los errores antes de continuar" -ForegroundColor Red
    Write-Host "Ver instrucciones en: URGENTE_PASOS_INMEDIATOS.txt" -ForegroundColor Yellow
    exit 1
}
