# Instrucciones: Modo Mantenimiento

## ¿Cómo activar el modo mantenimiento?

El modo mantenimiento bloquea el acceso a todos los visitantes excepto al administrador, permitiéndote hacer cambios sin que nadie los vea.

### Opción 1: Variable de Entorno en Render.com (Recomendado)

1. Ve a tu dashboard de Render.com
2. Selecciona tu servicio (web service)
3. Ve a la sección "Environment"
4. Agrega una nueva variable de entorno:
   - **Key**: `MAINTENANCE_MODE`
   - **Value**: `true`
5. Guarda los cambios
6. Render.com reiniciará automáticamente el servicio

### Opción 2: Variable de Entorno Local (.env)

Si estás trabajando localmente, agrega esta línea a tu archivo `.env`:

```
MAINTENANCE_MODE=true
```

## ¿Cómo desactivar el modo mantenimiento?

Simplemente cambia el valor de `MAINTENANCE_MODE` a `false` o elimina la variable de entorno.

## ¿Qué pasa cuando está activo?

- ✅ **Solo el administrador puede acceder** (desde `/login`)
- ✅ **Rutas de admin funcionan normalmente** (`/admin`, `/login`, etc.)
- ✅ **Archivos estáticos siguen funcionando** (CSS, imágenes, etc.)
- ❌ **Todos los demás visitantes ven la página de mantenimiento**
- ❌ **No pueden ver ningún cambio que estés haciendo**

## Página de Mantenimiento

Los visitantes verán una página profesional con:
- Mensaje de que el sitio está en mantenimiento
- Enlace para que administradores inicien sesión
- Diseño acorde a la marca Ubik2CR

## Notas Importantes

⚠️ **No olvides desactivar el modo mantenimiento** cuando termines de hacer cambios y quieras que el sitio sea público nuevamente.

✅ El modo mantenimiento es perfecto para:
- Hacer cambios grandes en la estructura
- Migraciones de base de datos
- Cambios de diseño importantes
- Pruebas sin afectar a usuarios
