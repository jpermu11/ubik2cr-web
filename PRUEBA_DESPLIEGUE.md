# 🧪 PRUEBA DE DESPLIEGUE - Verificar que los cambios se suben correctamente

## ✅ INDICADOR AGREGADO

He agregado un pequeño badge verde que dice **"✅ Prueba 1"** en la página principal.

Este indicador está ubicado:
- En la sección hero (parte superior de la página)
- Debajo del logo
- Con fondo verde y texto blanco
- Visible pero discreto

---

## 📋 CÓMO HACER LA PRUEBA

### PASO 1: Ver el indicador localmente (Opcional)

1. Ejecuta: `EJECUTAR.bat`
2. Abre: `http://localhost:5000`
3. Deberías ver el badge "✅ Prueba 1" arriba del logo

### PASO 2: Subir el cambio a producción

**Opción A: Si tienes Git configurado**
```batch
git add .
git commit -m "Prueba de despliegue - Indicador Prueba 1"
git push origin main
```

**Opción B: Usar el script asistente**
```batch
HACER_CAMBIO_SEGURO.bat
```
(Sigue las instrucciones del script)

### PASO 3: Esperar el despliegue

1. Ve a: https://render.com
2. Dashboard → ubik2cr-web
3. Verás un deploy en progreso (puede tardar 2-5 minutos)
4. Espera a que aparezca el checkmark verde ✅

### PASO 4: Verificar en producción

1. Abre tu sitio web en producción (tu dominio de Render.com)
2. Busca el badge verde "✅ Prueba 1" en la página principal
3. **Si lo ves:** ✅ **¡ÉXITO! Los cambios se están subiendo correctamente**
4. **Si no lo ves:** Espera 2-3 minutos más y recarga la página (Ctrl + F5)

---

## 🗑️ DESPUÉS DE LA PRUEBA: Quitar el indicador

Una vez que verifiques que funciona, quita el indicador:

1. Abre: `templates/index.html`
2. Busca esta línea (alrededor de la línea 80):
```html
<!-- INDICADOR DE PRUEBA - Verificar despliegues -->
<div style="background: rgba(76, 175, 80, 0.9); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 16px; font-size: 14px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
    ✅ Prueba 1
</div>
<br>
```

3. **Borra esas líneas** (el comentario, el div y el <br>)

4. Guarda el archivo

5. Sube el cambio:
```batch
git add .
git commit -m "Quitar indicador de prueba"
git push origin main
```

---

## 📝 RESUMEN

1. ✅ Indicador "Prueba 1" agregado
2. ⏳ Subir cambio con Git (commit + push)
3. ⏳ Esperar despliegue en Render (2-5 min)
4. 👀 Verificar en tu sitio web
5. 🗑️ Quitar indicador después de verificar

**Si ves "Prueba 1" en producción = Todo funciona correctamente ✅**
