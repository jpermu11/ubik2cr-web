# 🔄 RECREAR DEPLOY EN RENDER.COM

## ⚠️ INSTRUCCIONES PASO A PASO

### PASO 1: Eliminar el Deploy Actual

1. **Ve a Render.com** → Dashboard
2. **Encuentra el servicio** "ubik2cr-web" (o el nombre que tenga)
3. **Haz clic en el servicio**
4. **Ve a la pestaña "Settings"** (Configuración)
5. **Haz scroll hasta el final**
6. **Haz clic en "Delete Service"** (Eliminar Servicio)
7. **Confirma la eliminación**

### PASO 2: Crear Nuevo Deploy

1. **En Render.com Dashboard**, haz clic en **"New +"** → **"Web Service"**
2. **Conecta tu repositorio de GitHub:**
   - Si ya está conectado, selecciona "jpermu11/ubik2cr-web"
   - Si no, conecta tu cuenta de GitHub y selecciona el repositorio

3. **Configuración del Servicio:**
   - **Name:** `ubik2cr-web` (o el nombre que prefieras)
   - **Region:** Elige la región más cercana
   - **Branch:** `main`
   - **Root Directory:** (dejar vacío)

4. **Build & Deploy:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `sh -c "FLASK_APP=main.py flask db upgrade && gunicorn main:app"`

5. **Environment Variables (Variables de Entorno):**
   Agrega las siguientes variables:
   ```
   DATABASE_URL = (tu URL de base de datos PostgreSQL de Render)
   SESSION_SECRET = (genera un valor aleatorio)
   FLASK_ENV = production
   ```
   
   **Para obtener DATABASE_URL:**
   - Ve a tu base de datos PostgreSQL en Render
   - Haz clic en "Connections" (Conexiones)
   - Copia la "Internal Database URL" o "External Database URL"
   - **IMPORTANTE:** Si la URL tiene `?sslmode=require`, déjala así

6. **Plan:**
   - Elige el plan (Free, Starter, etc.)

7. **Haz clic en "Create Web Service"**

### PASO 3: Verificar el Deploy

1. **Espera a que el build termine** (puede tomar 2-5 minutos)
2. **Revisa los logs** para asegurarte de que no hay errores
3. **Visita tu URL** para verificar que funciona

---

## ✅ CHECKLIST ANTES DE CREAR EL DEPLOY

- [ ] Código en GitHub está actualizado (último push)
- [ ] `render.yaml` existe en el repositorio
- [ ] `requirements.txt` está actualizado
- [ ] `main.py` no intenta conectarse a DB durante el import (YA CORREGIDO ✅)
- [ ] Variables de entorno configuradas correctamente

---

## 🔧 CONFIGURACIÓN RECOMENDADA

### Build Command:
```bash
pip install -r requirements.txt
```

### Start Command:
```bash
sh -c "FLASK_APP=main.py flask db upgrade && gunicorn main:app"
```

### Variables de Entorno Mínimas:
```
DATABASE_URL = postgresql://user:pass@host:port/dbname
SESSION_SECRET = (valor aleatorio seguro)
FLASK_ENV = production
```

### Variables Opcionales (si las usas):
```
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
SMTP_USER = tu@email.com
SMTP_PASS = tu_password
SMTP_FROM = Ubik2CR <tu@email.com>
CLOUDINARY_CLOUD_NAME = tu_cloud_name
CLOUDINARY_API_KEY = tu_api_key
CLOUDINARY_API_SECRET = tu_api_secret
MAINTENANCE_MODE = false
```

---

## ⚠️ PROBLEMAS COMUNES

### Error: "could not translate host name"
- **Causa:** DATABASE_URL está apuntando a un hostname incorrecto
- **Solución:** Verifica que estés usando la URL interna de Render, o cambia a URL externa

### Error: "column does not exist"
- **Causa:** Las migraciones no se ejecutaron
- **Solución:** El `flask db upgrade` en el Start Command debería resolverlo

### Error: "ModuleNotFoundError"
- **Causa:** Falta una dependencia en `requirements.txt`
- **Solución:** Agrega la dependencia a `requirements.txt` y haz push

---

## 📝 NOTAS IMPORTANTES

1. **NO elimines la base de datos PostgreSQL** - Solo elimina el Web Service
2. **El código YA está corregido** - No intenta conectarse a DB durante el build
3. **Después de recrear**, el primer deploy puede tardar más porque ejecuta las migraciones
