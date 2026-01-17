# 🌐 CÓMO ABRIR LA APLICACIÓN EN LOCAL

## 🔍 URLs para Acceder

Cuando ejecutes `EJECUTAR.bat` o `python main.py`, la aplicación estará disponible en:

### ✅ URL Principal:
```
http://localhost:5000
```

### ✅ URL Alternativa:
```
http://127.0.0.1:5000
```

---

## 📝 PASOS PARA VERIFICAR

### 1. Verifica que la aplicación esté corriendo

Cuando ejecutas `EJECUTAR.bat`, deberías ver en la terminal algo como:

```
========================================
  INICIANDO LA APLICACION...
========================================

La aplicacion estara disponible en: http://localhost:5000

 * Running on http://0.0.0.0:5000
```

**Si ves esto, la aplicación está corriendo correctamente.**

### 2. Abre el navegador

Abre tu navegador (Chrome, Firefox, Edge) y ve a:

```
http://localhost:5000
```

**O copia y pega esto en la barra de direcciones:**
```
http://127.0.0.1:5000
```

---

## ⚠️ SI NO FUNCIONA

### Error 1: "No se puede acceder a este sitio"

**Solución:**
1. Verifica que la aplicación esté corriendo (mira la terminal)
2. Asegúrate de escribir bien la URL: `http://localhost:5000` (con `http://` al inicio)
3. Prueba con `http://127.0.0.1:5000`

### Error 2: "This site can't be reached"

**Solución:**
1. Verifica que no haya un error en la terminal
2. Cierra la terminal donde corre la app y vuelve a ejecutar `EJECUTAR.bat`
3. Asegúrate de que el puerto 5000 no esté siendo usado por otra aplicación

### Error 3: La terminal se cierra inmediatamente

**Solución:**
1. Abre CMD o PowerShell
2. Navega a la carpeta: `cd C:\Users\jperm\.cursor\flask-app`
3. Ejecuta: `EJECUTAR.bat`
4. Si ves errores, cópialos y compártelos

### Error 4: Error de base de datos

**Solución:**
1. Ejecuta en la terminal (con el entorno virtual activado):
   ```bash
   flask db upgrade
   ```

---

## 🔧 VERIFICAR QUE ESTÁ CORRIENDO

### Opción A: Ver en la Terminal

Cuando la app esté corriendo, verás algo como:

```
[INFO] Modelos de vehículos importados correctamente
 * Running on http://0.0.0.0:5000
```

### Opción B: Verificar con el Navegador

1. Abre el navegador
2. Ve a: `http://localhost:5000`
3. Si ves la página de Ubik2CR, **¡funciona!**

### Opción C: Verificar con PowerShell

Abre PowerShell y ejecuta:

```powershell
curl http://localhost:5000
```

Si obtienes código HTML, la app está corriendo.

---

## 📱 PÁGINAS IMPORTANTES

Una vez que funcione `http://localhost:5000`, puedes acceder a:

- **Página principal:** `http://localhost:5000/`
- **Login admin:** `http://localhost:5000/login`
- **Registro vendedor:** `http://localhost:5000/owner/registro`
- **Panel admin:** `http://localhost:5000/admin`
- **Panel vendedor:** `http://localhost:5000/panel`

---

## 🎯 EJEMPLO DE LO QUE DEBERÍAS VER

Cuando abres `http://localhost:5000` en el navegador, deberías ver:

1. **El logo de Ubik2CR** en la parte superior
2. **Un buscador de vehículos**
3. **La página principal** con el diseño azul y verde
4. **Navegación** en la parte superior

Si ves esto, **¡todo está funcionando correctamente!** ✅

---

## ❓ ¿AÚN NO FUNCIONA?

Si después de seguir estos pasos no funciona, dime:

1. ¿Qué ves en la terminal cuando ejecutas `EJECUTAR.bat`?
2. ¿Qué error aparece en el navegador?
3. ¿La terminal muestra algún mensaje de error?

Con esa información, puedo ayudarte mejor.
