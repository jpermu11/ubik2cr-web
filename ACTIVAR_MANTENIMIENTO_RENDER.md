# 🔒 Forzar Modo Mantenimiento en Render.com

## ✅ Estado Actual

El código está configurado para que **el modo mantenimiento esté ACTIVADO por defecto** cuando la aplicación corre en Render.com.

## 🎯 Cómo Verificar que Está Activado

1. **Ve a tu dashboard de Render.com**
2. **Selecciona tu servicio web** (Ubik2CR)
3. **Ve a la sección "Environment"**
4. **Verifica si existe la variable `MAINTENANCE_MODE`**

### Si NO existe la variable:
- ✅ **El modo mantenimiento está ACTIVADO** (valor por defecto)
- El sitio está offline para todos excepto admin

### Si existe y está en `false`:
- ❌ El sitio está online
- Cambiá el valor a `true` para activar mantenimiento

## 🔧 Cómo Activar/Desactivar Manualmente

### Para ACTIVAR modo mantenimiento (sitio offline):

1. Ve a Render.com → Tu servicio → Environment
2. Agrega o modifica la variable:
   - **Key**: `MAINTENANCE_MODE`
   - **Value**: `true`
3. Guarda los cambios
4. Render.com reiniciará automáticamente
5. El sitio quedará offline en 1-2 minutos

### Para DESACTIVAR modo mantenimiento (sitio online):

1. Ve a Render.com → Tu servicio → Environment
2. Agrega o modifica la variable:
   - **Key**: `MAINTENANCE_MODE`
   - **Value**: `false`
3. Guarda los cambios
4. Render.com reiniciará automáticamente
5. El sitio estará online en 1-2 minutos

## 📋 Resumen de Comportamiento

| Entorno | Modo Mantenimiento por Defecto | Cómo Cambiar |
|---------|-------------------------------|--------------|
| **Render.com** | ✅ **ACTIVADO** (true) | Variable `MAINTENANCE_MODE` |
| **Local** | ❌ Desactivado (false) | Variable `MAINTENANCE_MODE` o código |

## 🔍 Verificar que Funciona

1. **Sin estar logueado como admin:**
   - Visitá tu sitio: `https://tu-sitio.onrender.com`
   - Deberías ver la página de mantenimiento

2. **Como admin:**
   - Visitá: `https://tu-sitio.onrender.com/login`
   - Iniciá sesión con tus credenciales
   - Deberías poder acceder normalmente

## ⚠️ Importante

- **El modo mantenimiento está ACTIVADO por defecto en Render.com**
- **Solo el admin puede acceder** (desde `/login`)
- **Todos los demás verán la página de mantenimiento**
- **Para hacer el sitio público**, cambiá `MAINTENANCE_MODE` a `false`

## 🚀 Próximos Pasos

1. **Verificá que el modo mantenimiento esté activado** (debería estarlo por defecto)
2. **Hacé tus cambios** en desarrollo local
3. **Probá todo localmente** en `http://localhost:5000`
4. **Cuando esté listo**, hacé push y Render.com desplegará
5. **Para publicar**, cambiá `MAINTENANCE_MODE` a `false` en Render.com
