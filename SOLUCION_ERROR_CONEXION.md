# 🔧 Solución: "No se puede conectar a localhost:5000"

## ❌ El Problema

Si ves este error en Firefox:
> "No se puede conectar" / "Firefox no puede establecer una conexión con el servidor en localhost:5000"

**Significa que la aplicación Flask NO está corriendo.**

---

## ✅ Solución Paso a Paso

### Paso 1: Verificar si ejecutaste `run_local.bat`

**¿Ejecutaste el archivo `run_local.bat`?**

- ✅ **SÍ** → Ve al Paso 2
- ❌ **NO** → Ve al Paso 1.1

#### Paso 1.1: Ejecutar `run_local.bat` por primera vez

1. Abrí el Explorador de Archivos (Windows + E)
2. Navegá a: `C:\Users\jperm\.cursor\flask-app`
3. Buscá el archivo: `run_local.bat`
4. **Hacé DOBLE CLIC** en ese archivo
5. Se abrirá una ventana negra (CMD)
6. **ESPERÁ** a que termine (puede tardar varios minutos)
7. Cuando veas: "Aplicacion iniciada! Abri en tu navegador: http://localhost:5000"
8. **NO CIERRES esa ventana negra** (déjala abierta)
9. Recién ahí, abrí Firefox y escribí: `http://localhost:5000`

---

### Paso 2: Si ejecutaste `run_local.bat` pero sigue sin funcionar

**Revisá la ventana negra (CMD) que se abrió:**

#### ¿Qué mensajes ves?

**A) Si ves errores en rojo:**
- Mandame una captura de pantalla de la ventana negra
- O copiá y pegá el error completo aquí

**B) Si la ventana se cerró sola:**
- Probablemente hubo un error
- Volvé a ejecutar `run_local.bat`
- Esta vez, **NO cierres la ventana** y fijate qué mensaje sale al final

**C) Si ves "Running on http://127.0.0.1:5000":**
- ✅ La app está corriendo
- Probá con: `http://127.0.0.1:5000` en lugar de `localhost:5000`

---

### Paso 3: Verificar que la aplicación esté corriendo

**Abrí una nueva ventana de PowerShell y escribí:**

```powershell
netstat -ano | findstr :5000
```

**Si ves algo como:**
```
TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    12345
```

✅ **La aplicación está corriendo** → El problema es otro (ve al Paso 4)

**Si NO ves nada:**
❌ **La aplicación NO está corriendo** → Volvé al Paso 1

---

### Paso 4: Si la app está corriendo pero no carga

**Probá estas alternativas:**

1. **Usá `127.0.0.1` en lugar de `localhost`:**
   - Escribí en Firefox: `http://127.0.0.1:5000`

2. **Verificá que no haya otro programa usando el puerto 5000:**
   ```powershell
   netstat -ano | findstr :5000
   ```
   Si ves varios procesos, puede haber conflicto

3. **Probá con otro navegador:**
   - Chrome: `http://localhost:5000`
   - Edge: `http://localhost:5000`

4. **Verificá el firewall:**
   - Windows puede estar bloqueando la conexión
   - Permití Python/Flask en el firewall

---

## 🚀 Método Alternativo: Ejecutar Manualmente

Si `run_local.bat` no funciona, probá esto:

### 1. Abrí PowerShell

Presioná `Windows + R`, escribí `powershell`, presioná Enter

### 2. Ejecutá estos comandos (uno por uno):

```powershell
cd c:\Users\jperm\.cursor\flask-app
```

```powershell
python -m venv venv
```

```powershell
.\venv\Scripts\Activate.ps1
```

**Si te sale error de "execution policy":**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego volvé a:
```powershell
.\venv\Scripts\Activate.ps1
```

```powershell
pip install -r requirements.txt
```

```powershell
flask db upgrade
```

```powershell
python main.py
```

### 3. Deberías ver:

```
 * Running on http://127.0.0.1:5000
```

### 4. **NO CIERRES esta ventana**

### 5. Abrí Firefox y escribí: `http://localhost:5000`

---

## 📋 Checklist de Diagnóstico

Antes de pedir ayuda, verificá:

- [ ] ¿Ejecutaste `run_local.bat`?
- [ ] ¿La ventana negra (CMD) sigue abierta?
- [ ] ¿Ves el mensaje "Running on http://127.0.0.1:5000"?
- [ ] ¿Probaste con `http://127.0.0.1:5000` en lugar de `localhost`?
- [ ] ¿Probaste con otro navegador?
- [ ] ¿Hay errores en la ventana negra?

---

## 🆘 Si Nada Funciona

Mandame:

1. **Captura de pantalla de la ventana negra (CMD)** donde ejecutaste `run_local.bat`
2. **El último mensaje** que ves en esa ventana
3. **Qué pasos seguiste** exactamente

Con esa información te puedo ayudar mejor.

---

## 💡 Consejo Importante

**La aplicación Flask debe estar CORRIENDO para que puedas acceder a `localhost:5000`.**

Es como encender la TV antes de verla. La aplicación es el "encendido" y el navegador es la "pantalla".

**Siempre:**
1. Primero ejecutá `run_local.bat` (o `python main.py`)
2. Esperá a ver "Running on..."
3. **NO cierres esa ventana**
4. Recién ahí abrí el navegador
