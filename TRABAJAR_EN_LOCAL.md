# 💻 TRABAJAR EN LOCAL - Guía Completa

## 🎯 OBJETIVO

Trabajar localmente en el proyecto, sin conexión a Render, hasta que esté completamente listo para publicar.

---

## ✅ PASO 1: VERIFICAR REQUISITOS

### Instalar Python 3.8 o superior
1. Descarga Python desde: https://www.python.org/downloads/
2. **IMPORTANTE:** Durante la instalación, marca ✅ "Add Python to PATH"
3. Verifica la instalación:
   ```bash
   python --version
   ```

### Instalar Git (si no lo tienes)
1. Descarga desde: https://git-scm.com/downloads
2. Instala con la configuración por defecto

---

## ✅ PASO 2: CONFIGURAR EL PROYECTO LOCAL

### 1. Abrir Terminal en la carpeta del proyecto

```bash
cd C:\Users\jperm\.cursor\flask-app
```

### 2. Crear entorno virtual (si no existe)

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**En Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Si da error de permisos, ejecuta primero:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**O en CMD:**
```cmd
venv\Scripts\activate.bat
```

**O en Git Bash:**
```bash
source venv/Scripts/activate
```

Verás `(venv)` al inicio de la línea de comandos cuando esté activado.

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ✅ PASO 3: CONFIGURAR BASE DE DATOS LOCAL

### Opción A: Usar SQLite (Más fácil - Recomendado para desarrollo)

El proyecto ya está configurado para usar SQLite automáticamente si no hay `DATABASE_URL`.

**No necesitas hacer nada - funciona automáticamente.**

### Opción B: Usar PostgreSQL local (Opcional)

1. Instala PostgreSQL: https://www.postgresql.org/download/windows/
2. Crea una base de datos:
   ```sql
   CREATE DATABASE ubik2cr_local;
   ```
3. Crea un archivo `.env` en la carpeta del proyecto:
   ```
   DATABASE_URL=postgresql://usuario:password@localhost:5432/ubik2cr_local
   ```

---

## ✅ PASO 4: INICIALIZAR BASE DE DATOS

### Ejecutar migraciones:

```bash
flask db upgrade
```

Si es la primera vez, primero inicializa:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## ✅ PASO 5: CREAR ARCHIVO .env (Opcional pero recomendado)

Crea un archivo `.env` en la carpeta raíz del proyecto:

```env
# Base de datos (dejar vacío para usar SQLite local)
# DATABASE_URL=sqlite:///app.db

# Secret Key para sesiones (genera uno aleatorio)
SESSION_SECRET=tu_secret_key_super_seguro_aqui_cambiar

# Email (opcional - para recuperación de contraseña)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASS=tu_password_de_aplicacion
SMTP_FROM=Ubik2CR <tu_email@gmail.com>

# Cloudinary (opcional - para imágenes)
# CLOUDINARY_CLOUD_NAME=tu_cloud_name
# CLOUDINARY_API_KEY=tu_api_key
# CLOUDINARY_API_SECRET=tu_api_secret

# Modo mantenimiento (false para desarrollo)
MAINTENANCE_MODE=false

# Admin user (para acceso al panel admin)
ADMIN_USER=info@ubik2cr.com
ADMIN_PASS=UjifamKJ252319@
```

**Para generar SESSION_SECRET seguro:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## ✅ PASO 6: EJECUTAR LA APLICACIÓN

### Método 1: Usando el script .bat (Windows)

```bash
EJECUTAR.bat
```

### Método 2: Manualmente

```bash
# Asegúrate de estar en el entorno virtual
python main.py
```

### Método 3: Con Flask CLI

```bash
flask run
```

La aplicación estará disponible en: **http://localhost:5000**

---

## ✅ PASO 7: CREAR USUARIO ADMIN (Primera vez)

La primera vez que ejecutes la app, necesitas crear el usuario admin.

### Opción A: Desde la base de datos

```python
python crear_admin.py
```

O manualmente en Python:
```python
from models import db, Usuario
from werkzeug.security import generate_password_hash
from main import app

with app.app_context():
    admin = Usuario(
        email="info@ubik2cr.com",
        password=generate_password_hash("UjifamKJ252319@"),
        nombre="Admin",
        rol="admin"
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin creado!")
```

### Opción B: Usar el script crear_admin.py

Si no existe, lo crearemos.

---

## 📋 COMANDOS ÚTILES

### Activar entorno virtual:
```bash
venv\Scripts\activate
```

### Desactivar entorno virtual:
```bash
deactivate
```

### Instalar nueva dependencia:
```bash
pip install nombre_paquete
pip freeze > requirements.txt  # Actualizar requirements.txt
```

### Ver logs de la aplicación:
Los logs aparecen directamente en la terminal donde ejecutas la app.

### Ver estructura de base de datos:
```bash
flask db current
flask db history
```

### Crear nueva migración:
```bash
flask db migrate -m "Descripción del cambio"
flask db upgrade
```

---

## 🛠️ ESTRUCTURA DEL PROYECTO

```
flask-app/
├── main.py              # Aplicación principal
├── models.py            # Modelos de base de datos
├── requirements.txt     # Dependencias Python
├── .env                 # Variables de entorno (crear manualmente)
├── venv/                # Entorno virtual (crear con python -m venv venv)
├── migrations/          # Migraciones de base de datos
├── templates/           # Plantillas HTML
├── static/              # Archivos estáticos (CSS, JS, imágenes)
│   ├── uploads/         # Imágenes subidas
│   └── data/            # Datos JSON
└── EJECUTAR.bat         # Script para ejecutar en Windows
```

---

## ⚠️ PROBLEMAS COMUNES

### Error: "No module named 'flask'"
**Solución:** Activa el entorno virtual y ejecuta `pip install -r requirements.txt`

### Error: "Could not locate a Flask application"
**Solución:** Ejecuta `set FLASK_APP=main.py` (Windows) o `export FLASK_APP=main.py` (Linux/Mac)

### Error: "Address already in use"
**Solución:** Cierra la aplicación anterior o cambia el puerto:
```bash
flask run --port 5001
```

### Error: "Database is locked" (SQLite)
**Solución:** Cierra todas las conexiones a la base de datos y vuelve a intentar

### La aplicación no se actualiza al hacer cambios
**Solución:** Usa modo debug (ya está configurado en `main.py`), reinicia la aplicación

---

## 🚀 FLUJO DE TRABAJO RECOMENDADO

1. **Activar entorno virtual** cada vez que trabajes
2. **Ejecutar la app** con `python main.py` o `EJECUTAR.bat`
3. **Hacer cambios** en el código
4. **Probar localmente** en http://localhost:5000
5. **Verificar que funciona** antes de hacer commit
6. **Hacer commit y push** solo cuando esté listo
7. **Cuando esté completamente listo** → Desplegar a Render

---

## 📝 NOTAS IMPORTANTES

- ✅ **NO** subas el archivo `.env` a GitHub (está en .gitignore)
- ✅ **NO** subas `venv/` a GitHub
- ✅ **SÍ** puedes trabajar sin conexión a internet
- ✅ **La base de datos SQLite** se crea automáticamente en `app.db`
- ✅ **Las migraciones** se aplican automáticamente al iniciar

---

## 🎯 SIGUIENTE PASO

Una vez que todo funcione localmente y el proyecto esté listo, usaremos `RECREAR_DEPLOY_RENDER.md` para desplegar a producción.

**¡Empecemos a trabajar en local! 🚀**
