# 🚀 Desarrollo Local - Ver Cambios Antes de Publicar

## ¿Cómo funciona?

**Desarrollo Local** = Correr la aplicación en tu computadora para ver los cambios **antes** de publicarlos en Render.com.

## ⚡ Inicio Rápido (Windows)

### Opción 1: Script Automático (Más Fácil)

1. **Doble clic en `run_local.bat`**
2. **Esperá a que termine de instalar**
3. **Abrí tu navegador en:** `http://localhost:5000`
4. **¡Listo!** Verás todos tus cambios en tiempo real

### Opción 2: Manual (Si el script no funciona)

```powershell
# 1. Abrir terminal en la carpeta del proyecto
cd c:\Users\jperm\.cursor\flask-app

# 2. Crear entorno virtual (solo la primera vez)
python -m venv venv

# 3. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear archivo .env (si no existe)
# Copiá el contenido de abajo y guardalo como .env

# 6. Inicializar base de datos
flask db upgrade

# 7. Correr aplicación
python main.py
```

## 📝 Archivo .env (Configuración Local)

Creá un archivo llamado `.env` en la raíz del proyecto con:

```env
SECRET_KEY=clave-secreta-para-desarrollo-local
DATABASE_URL=sqlite:///local.db
MAINTENANCE_MODE=false
ADMIN_USER=tu_usuario
ADMIN_PASSWORD=tu_password
```

**Nota:** Para desarrollo local, podés usar SQLite (más fácil) o PostgreSQL.

## ✅ Ventajas del Desarrollo Local

- ✅ **Ver cambios instantáneamente** (sin esperar deploy)
- ✅ **Modo mantenimiento desactivado** (podés ver todo)
- ✅ **Probar sin afectar producción**
- ✅ **Debug más fácil** (ver errores en consola)
- ✅ **No consume recursos de Render**

## 🔄 Flujo de Trabajo Recomendado

```
1. Hacé cambios en tu código
   ↓
2. Probá localmente en http://localhost:5000
   ↓
3. Cuando esté todo bien, hacé push a GitHub
   ↓
4. Render.com desplegará automáticamente
```

## 🛠️ Comandos Útiles

```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar nueva dependencia
pip install nombre_paquete
pip freeze > requirements.txt

# Ver logs de errores
python main.py

# Correr en modo debug (recarga automática al guardar)
flask run --debug --port 5000
```

## ❓ Solución de Problemas

### "flask no se reconoce"
- Asegurate de tener el entorno virtual activado
- Instalá Flask: `pip install flask`

### "Error de base de datos"
- Verificá que `DATABASE_URL` esté correcto en `.env`
- Ejecutá: `flask db upgrade`

### "Puerto 5000 ocupado"
- Usá otro puerto: `flask run --port 5001`
- O cambiá en `main.py`: `port = int(os.environ.get("PORT", 5001))`

### "No se puede activar el entorno virtual"
- Probá: `.\venv\Scripts\activate` (sin .ps1)
- O: `python -m venv venv --upgrade-deps`

## 📌 Notas Importantes

- **Modo mantenimiento:** En local está **desactivado** por defecto
- **Base de datos:** Los datos locales son independientes de producción
- **Cambios:** Solo se ven localmente hasta que hagas push
- **Render.com:** Sigue en modo mantenimiento hasta que lo desactives

## 🎯 Próximos Pasos

1. **Corré la app localmente** con `run_local.bat`
2. **Hacé tus cambios** en el código
3. **Probá todo** en `http://localhost:5000`
4. **Cuando esté listo**, hacé push y Render.com lo publicará
