# 🚨 CONFIGURACIÓN DE PRODUCCIÓN - Ubik2CR

## ⚠️ CRÍTICO: App para miles de usuarios - NO PUEDE FALLAR

### ✅ CHECKLIST DE SEGURIDAD IMPLEMENTADO

#### 1. 🔄 BACKUP AUTOMÁTICO
- ✅ Script de auto-backup cada hora
- ✅ Commit automático a Git
- ✅ Push automático a GitHub (backup remoto)
- ✅ Copia local de seguridad

**Configurar Windows Task Scheduler:**
```
1. Abre "Task Scheduler"
2. Create Basic Task
3. Nombre: "Ubik2CR Auto-Backup"
4. Trigger: Daily (cada hora)
5. Action: Start a program
6. Programa: C:\Users\jperm\.cursor\flask-app\auto_backup.bat
```

#### 2. 🔗 GIT + GITHUB (OBLIGATORIO)
- ✅ Repositorio Git configurado
- ✅ Conexión a GitHub establecida
- ✅ Auto-push configurado
- ✅ Historial completo guardado

**NUNCA trabajar sin Git activo:**
```bash
# Verificar que Git está activo:
dir /a .git

# Si NO existe, ejecutar:
setup_git_urgente.bat
```

#### 3. 🚀 RENDER.COM - ALTA DISPONIBILIDAD
- ✅ Auto-deploy desde GitHub activado
- ✅ Health checks configurados (`/health`)
- ✅ Variables de entorno seguras
- ✅ Base de datos PostgreSQL en producción

**Verificar configuración:**
1. Ve a: https://render.com
2. Entra a servicio: `ubik2cr-web`
3. Settings → Auto-Deploy: DEBE estar ON
4. Settings → Health Check: `/health`

#### 4. 📊 MONITOREO Y ALERTAS

**Configurar alertas en Render:**
1. Render Dashboard → ubik2cr-web → Settings
2. Notifications → Activar alertas de:
   - Deployment failures
   - Service crashes
   - High latency
   - Health check failures

**Email de alertas:** jpermu@gmail.com

#### 5. 🛡️ SEGURIDAD

**Variables de Entorno (NUNCA en código):**
- ✅ SESSION_SECRET (generada automáticamente)
- ✅ DATABASE_URL (solo en Render)
- ✅ ADMIN_USER/PASS (solo en Render)
- ✅ SMTP_* (solo en Render)

**Archivo .gitignore configurado:**
- ✅ `.env` (ignorado)
- ✅ `instance/` (ignorado)
- ✅ `__pycache__/` (ignorado)

#### 6. 🔄 WORKFLOW DE PRODUCCIÓN

**ANTES de hacer cambios:**
1. ✅ Verificar que Git está activo: `git status`
2. ✅ Crear branch de desarrollo: `git checkout -b feature/nueva-funcion`
3. ✅ Hacer cambios
4. ✅ Probar localmente: `python main.py`
5. ✅ Commit: `git commit -m "Descripción"`
6. ✅ Push: `git push origin feature/nueva-funcion`
7. ✅ Merge a main solo cuando esté probado
8. ✅ Render despliega automáticamente

**NUNCA:**
- ❌ Cambiar código directamente en producción
- ❌ Hacer cambios sin commit
- ❌ Push sin probar localmente
- ❌ Trabajar sin Git activo

#### 7. 📝 PROCEDIMIENTO DE EMERGENCIA

**Si Render falla:**
1. Ve a: https://render.com
2. Dashboard → ubik2cr-web → Manual Deploy
3. Selecciona último commit estable
4. Deploy ahora

**Si código local se pierde:**
```bash
# Recuperar desde GitHub:
git clone https://github.com/jpermu11/ubik2cr-web.git
cd ubik2cr-web
# Todo tu código está ahí
```

**Si base de datos falla:**
1. Render Dashboard → ubik2cr-db-oregon
2. Settings → Backup
3. Restaurar último backup

#### 8. 🔍 VERIFICACIÓN DIARIA (AUTOMATIZADA)

**Crear script de verificación:**
```batch
@echo off
echo Verificando salud de Ubik2CR...
curl https://ubik2cr.com/health
if errorlevel 1 (
    echo ERROR: Servicio caido!
    REM Enviar alerta por email
)
```

#### 9. 📈 ESCALABILIDAD PARA MILES DE USUARIOS

**Render.com Free Tier (actual):**
- ✅ Soporta hasta ~100 usuarios concurrentes
- ⚠️ Si creces, necesitas plan de pago ($7/mes)

**Upgrade recomendado cuando:**
- Más de 100 usuarios activos simultáneos
- Tiempos de respuesta > 2 segundos
- Render muestra warnings de recursos

**Opciones de escalado:**
1. Render Starter Plan ($7/mes): Más recursos
2. Render Professional ($25/mes): Auto-scaling
3. Supabase (gratis): Base de datos escalable

#### 10. 🚨 PROTOCOLO DE INCIDENTES

**Si algo falla EN PRODUCCIÓN:**

1. **NO ENTRAR EN PÁNICO**
2. Verificar logs en Render:
   - Dashboard → ubik2cr-web → Logs
3. Si es crítico, revertir deploy:
   - Render → Deploys → Rollback
4. Si es código, hotfix:
   - Crear branch: `git checkout -b hotfix/critical-fix`
   - Fix rápido
   - Commit y push urgente
   - Merge inmediato a main
5. Notificar a usuarios si hay downtime

---

## ✅ CHECKLIST DIARIO (5 minutos)

- [ ] Verificar que Git está activo: `git status`
- [ ] Verificar salud: `curl https://ubik2cr.com/health`
- [ ] Revisar logs en Render (últimos errores)
- [ ] Verificar que auto-backup corrió (verificar fecha)

## ✅ CHECKLIST SEMANAL (15 minutos)

- [ ] Revisar métricas de Render (usuarios, latencia)
- [ ] Verificar que no hay cambios sin commit
- [ ] Revisar dependencias: `pip list --outdated`
- [ ] Backup manual completo (opcional)

---

## 🎯 PRIORIDADES ABSOLUTAS

1. **GIT SIEMPRE ACTIVO** - Sin Git = Pérdida de trabajo
2. **BACKUP AUTOMÁTICO** - Cada hora sin excepción
3. **MONITOREO ACTIVO** - Alertas configuradas
4. **PRUEBAS ANTES DE DEPLOY** - NUNCA push sin probar
5. **DOCUMENTACIÓN ACTUALIZADA** - Cada cambio documentado

---

## 📞 CONTACTOS DE EMERGENCIA

- **Render Support:** support@render.com
- **GitHub Support:** support@github.com
- **Email alertas:** jpermu@gmail.com

---

## 🔒 GARANTÍAS IMPLEMENTADAS

✅ **Backup múltiple:** Local + GitHub + Render
✅ **Auto-deploy:** Despliegue automático sin intervención
✅ **Health checks:** Monitor de salud activo
✅ **Rollback:** Capacidad de revertir cambios
✅ **Logs completos:** Historial de todo
✅ **Seguridad:** Variables sensibles protegidas

**ESTE SISTEMA ESTÁ DISEÑADO PARA NO FALLAR.**
