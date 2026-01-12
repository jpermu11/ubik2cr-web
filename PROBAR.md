# 🧪 Guía para Probar la Aplicación

## Paso 1: Verificar Python

Abre PowerShell o CMD y ejecuta:
```bash
python --version
```

**Si no tienes Python instalado:**
1. Descarga Python desde: https://www.python.org/downloads/
2. Durante la instalación, **marca la opción "Add Python to PATH"**
3. Reinicia tu terminal después de instalar

## Paso 2: Instalar Dependencias

Una vez que Python funcione, ejecuta estos comandos:

```bash
# Ir a la carpeta del proyecto
cd C:\Users\jperm\.cursor\flask-app

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual (Windows PowerShell)
venv\Scripts\Activate.ps1

# Si te da error de política, ejecuta primero:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# O en CMD normal:
# venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

## Paso 3: Configurar Base de Datos

Para desarrollo local, **NO necesitas configurar nada**. La app usará SQLite automáticamente.

Si quieres usar PostgreSQL, crea un archivo `.env` con:
```
DATABASE_URL=postgresql://usuario:password@host:puerto/database
```

## Paso 4: Inicializar Base de Datos

```bash
# Inicializar migraciones (solo la primera vez)
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade
```

## Paso 5: Configurar Variables de Entorno (Opcional)

Crea un archivo `.env` en la carpeta `flask-app` con:

```
SESSION_SECRET=mi-clave-secreta-123
ADMIN_USER=admin
ADMIN_PASS=admin123
PORT=5000
```

**Nota:** Para desarrollo, puedes dejar estas vacías y usar los valores por defecto.

## Paso 6: Ejecutar la Aplicación

```bash
python main.py
```

O:
```bash
flask run
```

## Paso 7: Probar la Aplicación

1. Abre tu navegador en: `http://localhost:5000`
2. Deberías ver la página principal de Ubik2CR
3. Prueba:
   - Ir a `/cuenta` para crear una cuenta de dueño
   - Ir a `/login` para iniciar sesión como admin (usando ADMIN_USER/ADMIN_PASS)
   - Publicar un negocio desde `/publicar` (después de crear cuenta)

## ⚠️ Problemas Comunes

### Error: "DATABASE_URL no está configurado"
- **Solución:** La app ahora usa SQLite por defecto. Si ves este error, actualiza `main.py` o crea un `.env` con `DATABASE_URL=sqlite:///app.db`

### Error: "ModuleNotFoundError"
- **Solución:** Ejecuta `pip install -r requirements.txt` de nuevo

### Error: "flask: command not found"
- **Solución:** Asegúrate de tener el entorno virtual activado y las dependencias instaladas

### Error: "Permission denied" en Windows
- **Solución:** Ejecuta PowerShell como Administrador o usa CMD normal

## 📝 Nota sobre el Logo

Necesitas agregar un logo en `static/uploads/logo.png`. Si no lo tienes:
- Puedes usar cualquier imagen PNG
- O crear un placeholder temporal

## ✅ Checklist de Prueba

- [ ] Python instalado y funcionando
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos inicializada (`flask db upgrade`)
- [ ] Aplicación ejecutándose (`python main.py`)
- [ ] Página principal carga en el navegador
- [ ] Puedes crear una cuenta de dueño
- [ ] Puedes iniciar sesión como admin

