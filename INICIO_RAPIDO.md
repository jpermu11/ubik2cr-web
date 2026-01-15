# 🚀 INICIO RÁPIDO - Ver Cambios Localmente

## ⚡ Método Más Fácil (1 Clic)

**Simplemente hacé doble clic en: `run_local.bat`**

Eso es todo. El script hará todo automáticamente:
- ✅ Creará el entorno virtual (si no existe)
- ✅ Instalará las dependencias
- ✅ Inicializará la base de datos
- ✅ Iniciará la aplicación

Luego abrí tu navegador en: **http://localhost:5000**

---

## 📋 Si el Script No Funciona (Método Manual)

### Paso 1: Abrir Terminal

1. Presioná `Windows + R`
2. Escribí: `powershell`
3. Presioná Enter

### Paso 2: Ir a la Carpeta del Proyecto

```powershell
cd c:\Users\jperm\.cursor\flask-app
```

### Paso 3: Crear Entorno Virtual (Solo Primera Vez)

```powershell
python -m venv venv
```

### Paso 4: Activar Entorno Virtual

```powershell
.\venv\Scripts\Activate.ps1
```

**Si te sale error de "execution policy", escribí primero:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego volvé a intentar el comando de arriba.

Deberías ver `(venv)` al inicio de la línea.

### Paso 5: Instalar Dependencias

```powershell
pip install -r requirements.txt
```

Esto puede tardar varios minutos la primera vez.

### Paso 6: Inicializar Base de Datos

```powershell
flask db upgrade
```

### Paso 7: Ejecutar la Aplicación

```powershell
python main.py
```

Deberías ver algo como:
```
 * Running on http://127.0.0.1:5000
```

**¡NO CIERRES ESTA VENTANA!** Déjala abierta.

### Paso 8: Abrir en el Navegador

1. Abrí tu navegador (Chrome, Edge, Firefox, etc.)
2. En la barra de direcciones escribí: **http://localhost:5000**
3. Presioná Enter

---

## 🎯 URLs Importantes para Ver los Cambios

Una vez que la app esté corriendo, podés visitar:

- **Página Principal (Búsqueda de Vehículos):**
  - http://localhost:5000/

- **Publicar Vehículo:**
  - http://localhost:5000/vehiculos/publicar

- **Crear Cuenta / Iniciar Sesión:**
  - http://localhost:5000/cuenta

- **Panel de Administración:**
  - http://localhost:5000/admin
  - (Necesitás iniciar sesión como admin)

---

## ⚠️ Solución de Problemas

### Error: "python no se reconoce"
- Instalá Python desde: https://www.python.org/downloads/
- Durante la instalación, **marcá "Add Python to PATH"**
- Reiniciá la terminal

### Error: "flask no se reconoce"
- Asegurate de que el entorno virtual esté activado (deberías ver `(venv)`)
- Ejecutá: `pip install flask flask-migrate`

### Error: "No module named 'models'"
- Asegurate de estar en la carpeta correcta: `c:\Users\jperm\.cursor\flask-app`
- Verificá que `models.py` exista en esa carpeta

### Error: "Port 5000 already in use"
- Alguien más está usando el puerto 5000
- Cerralo o cambiá el puerto en `main.py`

### La página no carga
- Verificá que la ventana de PowerShell/CMD siga abierta
- Verificá que no haya errores en esa ventana
- Probá con: http://127.0.0.1:5000 en lugar de localhost

---

## 🔄 Para Ver Cambios Nuevos

1. **Yo hago cambios** en el código
2. **Vos corrés** `run_local.bat` (o `python main.py` si ya tenés todo instalado)
3. **Visitás** http://localhost:5000
4. **Probás** los cambios
5. **Me decís** qué ajustar

**Nota:** Si la app ya está corriendo, podés recargar la página (F5) para ver cambios en templates. Para cambios en Python, necesitás reiniciar la app (Ctrl+C y volver a correr `python main.py`).

---

## ✅ Checklist Rápido

- [ ] Python instalado
- [ ] Doble clic en `run_local.bat` (o seguí método manual)
- [ ] Ver `(venv)` en la terminal
- [ ] Ver mensaje "Running on http://127.0.0.1:5000"
- [ ] Abrir http://localhost:5000 en el navegador
- [ ] ¡Ver la página funcionando!

---

## 📞 Si Nada Funciona

Mandame un mensaje con:
1. El error exacto que te sale
2. Una captura de pantalla de la terminal
3. Qué paso estás intentando hacer

¡Y te ayudo a solucionarlo!
