# Guía: Desarrollo Local - Ver Cambios Antes de Publicar

## ¿Por qué desarrollo local?

Te permite ver todos los cambios en tu computadora **antes** de hacer push a Render.com. Así podés probar todo sin afectar el sitio en producción.

## Pasos para correr la aplicación localmente

### 1. Instalar Python (si no lo tenés)

- Descargá Python 3.9+ desde: https://www.python.org/downloads/
- Durante la instalación, marcá "Add Python to PATH"

### 2. Abrir terminal en la carpeta del proyecto

```powershell
cd c:\Users\jperm\.cursor\flask-app
```

### 3. Crear entorno virtual (solo la primera vez)

```powershell
python -m venv venv
```

### 4. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

Si te da error, probá:
```powershell
.\venv\Scripts\activate
```

### 5. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 6. Configurar variables de entorno

Creá un archivo `.env` en la raíz del proyecto con:

```env
SECRET_KEY=tu_secret_key_aqui
DATABASE_URL=postgresql://usuario:password@localhost/ubik2cr
MAINTENANCE_MODE=false
ADMIN_USER=tu_usuario_admin
ADMIN_PASSWORD=tu_password_admin
```

**Para la base de datos local:**
- Podés usar SQLite (más fácil) o PostgreSQL
- Para SQLite, usá: `DATABASE_URL=sqlite:///local.db`

### 7. Inicializar la base de datos

```powershell
flask db upgrade
```

### 8. Correr la aplicación

```powershell
python main.py
```

O:

```powershell
flask run
```

### 9. Abrir en el navegador

- Abrí: `http://localhost:5000`
- Verás todos tus cambios en tiempo real

## Ventajas

✅ **Ver cambios instantáneamente** sin esperar deploy
✅ **Probar sin afectar producción**
✅ **Modo mantenimiento desactivado localmente**
✅ **Debug más fácil** (ver errores en consola)
✅ **No consume recursos de Render**

## Flujo de trabajo recomendado

1. **Hacé cambios** en tu código
2. **Probá localmente** en `http://localhost:5000`
3. **Cuando esté todo bien**, hacé push a GitHub
4. **Render.com desplegará** automáticamente

## Comandos útiles

```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar nueva dependencia
pip install nombre_paquete
pip freeze > requirements.txt

# Ver logs de errores
python main.py

# Correr en modo debug (recarga automática)
flask run --debug
```

## Solución de problemas

**Error: "flask no se reconoce"**
- Asegurate de tener el entorno virtual activado
- Instalá Flask: `pip install flask`

**Error de base de datos**
- Verificá que `DATABASE_URL` esté correcto en `.env`
- Ejecutá: `flask db upgrade`

**Puerto 5000 ocupado**
- Usá otro puerto: `flask run --port 5001`
