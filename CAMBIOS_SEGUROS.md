# 🔒 GUÍA: HACER CAMBIOS SEGUROS SIN PERDER DATOS

## ✅ GARANTÍA: Tus datos de usuarios están PROTEGIDOS

**Lo más importante:** Tus datos de usuarios están en una base de datos PostgreSQL separada en Render.com. **NO se pueden perder** solo por modificar código aquí.

---

## 📋 PROCESO SEGURO PARA HACER CAMBIOS

### PASO 1: HACER BACKUP ANTES DE CAMBIAR (AUTOMÁTICO)

Antes de hacer cualquier cambio, el sistema ya tiene protección:

1. **Backup automático** cada hora (auto_backup.bat)
2. **Git guarda todo** el historial
3. **Render.com tiene backups** automáticos de la base de datos

**Acción:** Ejecuta este comando antes de cambiar código:
```batch
auto_backup.bat
```

---

### PASO 2: MODIFICAR EL CÓDIGO (LOCAL)

1. Modifica `main.py` o `models.py` en tu computadora
2. **NO toques la base de datos directamente**
3. Si necesitas agregar/eliminar campos en las tablas:
   - Modifica `models.py`
   - Las migraciones harán el resto automáticamente

---

### PASO 3: CREAR MIGRACIÓN (SI CAMBIASTE models.py)

**⚠️ SOLO si modificaste models.py (agregaste/eliminaste campos):**

```batch
flask db migrate -m "Descripción de los cambios"
```

Esto **NO borra datos**. Solo crea un archivo que dice "agregar este campo" o "eliminar esta columna".

**Ejemplo de migración segura:**
- ✅ Agregar un nuevo campo: `telefono_adicional = db.Column(...)`
- ✅ Agregar una nueva tabla: `class NuevoModelo(db.Model): ...`
- ❌ **NUNCA** eliminar campos que tienen datos (solo si estás seguro que está vacío)

---

### PASO 4: PROBAR LOCALMENTE

1. Aplica la migración localmente:
```batch
flask db upgrade
```

2. Ejecuta la aplicación:
```batch
EJECUTAR.bat
```

3. Prueba TODO lo que modificaste:
   - Login funciona
   - Registro funciona
   - Ver negocios funciona
   - Agregar negocios funciona
   - Todo lo que tocaste funciona

**✅ Si todo funciona:** Continúa al siguiente paso
**❌ Si algo falla:** Revierte los cambios (ver PASO 7)

---

### PASO 5: HACER COMMIT (GUARDAR CAMBIOS)

Cuando estés seguro de que todo funciona:

```batch
git add .
git commit -m "Agregué: [descripción de cambios]"
git push origin main
```

---

### PASO 6: DESPLEGAR A PRODUCCIÓN (AUTOMÁTICO)

**Render.com despliega automáticamente** cuando haces push a GitHub.

1. Render detecta el push
2. Render ejecuta `flask db upgrade` automáticamente
3. La nueva versión se despliega
4. **Los datos de usuarios NO se pierden** porque:
   - Las migraciones solo AGREGAN/ALTERAN campos
   - Los datos existentes se mantienen
   - Las tablas existentes no se borran

**Tiempo de despliegue:** 2-5 minutos

**Verificar:** Ve a https://render.com y revisa el deploy

---

### PASO 7: SI ALGO SALE MAL (REVERTIR)

Si después de desplegar algo falla:

**Opción 1: Revertir el código (Rápido)**

En Render.com:
1. Dashboard → ubik2cr-web
2. Manual Deploy
3. Selecciona el commit anterior (el que funcionaba)
4. Deploy Now

**Opción 2: Revertir migración (Solo si es necesario)**

**⚠️ Solo si agregaste una migración que causa problemas:**

```batch
flask db downgrade -1
```

Esto revierte la última migración.

---

## 🛡️ PROTECCIONES QUE TIENES

### 1. **Migraciones Protegen Datos**
- Las migraciones de Flask-Migrate **NO borran datos**
- Solo agregan/alteran campos
- Los datos existentes se mantienen

### 2. **Base de Datos Separada**
- Tu base de datos está en Render.com (PostgreSQL)
- **NO está en tu computadora**
- Modificar código local NO toca los datos de producción

### 3. **Backups Automáticos**
- Git guarda cada versión
- Render.com hace backups de la base de datos
- auto_backup.bat guarda código cada hora

### 4. **Despliegue Seguro**
- Render ejecuta migraciones automáticamente
- Si una migración falla, el despliegue se detiene
- La versión anterior sigue funcionando

---

## 📝 EJEMPLOS DE CAMBIOS SEGUROS

### ✅ AGREGAR UNA NUEVA FUNCIÓN (SIN TOCAR BASE DE DATOS)

**Ejemplo:** Agregar página de contacto

1. Modifica `main.py` (agrega ruta nueva)
2. Modifica `templates/` (agrega HTML nuevo)
3. Prueba localmente
4. Commit y push
5. **NO necesitas migración** porque no cambiaste models.py

### ✅ AGREGAR UN CAMPO NUEVO A UNA TABLA

**Ejemplo:** Agregar campo "telefono_adicional" a Negocio

1. Modifica `models.py`:
```python
telefono_adicional = db.Column(db.String(20), nullable=True)
```

2. Crea migración:
```batch
flask db migrate -m "Agregar telefono_adicional a Negocio"
```

3. Prueba localmente:
```batch
flask db upgrade
EJECUTAR.bat
```

4. Si funciona, commit y push
5. Render despliega automáticamente

**⚠️ IMPORTANTE:** Usa `nullable=True` para campos nuevos en tablas existentes, así los registros antiguos no causan error.

### ✅ AGREGAR UNA NUEVA TABLA

**Ejemplo:** Agregar tabla "Productos"

1. Modifica `models.py` (agrega nuevo modelo)
2. Crea migración:
```batch
flask db migrate -m "Agregar tabla Productos"
```

3. Prueba y despliega igual que arriba

---

## ❌ QUÉ NO HACER

1. **NO eliminar campos** que tienen datos sin migrar primero
2. **NO hacer cambios directamente en la base de datos de producción**
3. **NO hacer push sin probar localmente primero**
4. **NO modificar migraciones ya aplicadas** (crea una nueva)

---

## 🔍 VERIFICAR QUE TODO ESTÁ BIEN

### Después de cada cambio:

1. **Probar localmente:**
   - Login funciona
   - Registro funciona
   - Ver datos funciona
   - Agregar datos funciona

2. **Verificar en Render:**
   - El deploy se completó (green checkmark)
   - No hay errores en logs
   - La aplicación carga normalmente

3. **Verificar usuarios:**
   - Login funciona en producción
   - Los datos se ven correctamente
   - No hay errores 500

---

## 🆘 EMERGENCIAS

### Si algo falla en producción:

1. **NO PANIQUEES** - Los datos están seguros
2. Revisa logs en Render.com
3. Revierte el último deploy (Manual Deploy → commit anterior)
4. Si necesitas ayuda, revisa los logs de error

---

## 📞 RESUMEN RÁPIDO

1. **Modificar código:** ✅ SEGURO (solo afecta código)
2. **Agregar campos/tablas:** ✅ SEGURO (usar migraciones)
3. **Probar localmente:** ✅ OBLIGATORIO
4. **Hacer commit y push:** ✅ SEGURO
5. **Render despliega:** ✅ AUTOMÁTICO Y SEGURO

**Tus datos de usuarios están PROTEGIDOS porque:**
- Base de datos separada en Render.com
- Migraciones no borran datos
- Backups automáticos
- Puedes revertir cualquier cambio

---

**Puedes modificar tu aplicación con confianza. Las migraciones y el sistema de despliegue protegen tus datos.**
