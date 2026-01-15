# 🚗 Plan de Limpieza y Migración: Ubik2CR → Plataforma de Venta de Vehículos

## 📋 Situación Actual

- **Sistema actual:** Directorio de negocios locales
- **Sistema objetivo:** Plataforma de venta de vehículos usados (estilo Crautos)
- **Credenciales admin:** Se validan contra variables de entorno (`ADMIN_USER`, `ADMIN_PASS`)
- **Base de datos:** Contiene negocios, noticias, ofertas, mensajes, etc.

## 🎯 Objetivos

1. ✅ **Mantener credenciales de administrador** (variables de entorno)
2. ✅ **Limpiar toda la base de datos** (excepto estructura)
3. ✅ **Implementar sistema de vehículos** (usuarios regulares + agencias)
4. ✅ **Migrar sin perder acceso admin**

## 💡 Opciones para Limpiar la Base de Datos

### **Opción 1: Script de Limpieza (RECOMENDADO) ⭐**

**Ventajas:**
- ✅ Mantiene la estructura de tablas
- ✅ Limpia solo los datos
- ✅ Preserva índices y relaciones
- ✅ Más seguro (reversible)

**Cómo funciona:**
- Crear un script que elimine todos los registros de tablas específicas
- Mantener la tabla `usuarios` pero limpiarla (excepto si hay admin ahí)
- Ejecutar desde el panel de admin

### **Opción 2: Migración de Base de Datos**

**Ventajas:**
- ✅ Limpieza completa y estructurada
- ✅ Crea nuevas tablas para vehículos
- ✅ Elimina tablas antiguas

**Desventajas:**
- ⚠️ Más complejo
- ⚠️ Requiere cuidado con las migraciones

### **Opción 3: Backup y Recreación**

**Ventajas:**
- ✅ Base de datos completamente limpia
- ✅ Solo las tablas necesarias

**Desventajas:**
- ⚠️ Requiere recrear estructura
- ⚠️ Más trabajo manual

## 🔐 Sobre las Credenciales de Admin

**Estado actual:**
- Las credenciales NO están en la base de datos
- Se validan contra variables de entorno (`ADMIN_USER`, `ADMIN_PASS`)
- **NO se perderán** al limpiar la BD ✅

**Recomendación:**
- Mantener el sistema actual (variables de entorno)
- O crear un usuario admin en la BD con rol especial

## 📊 Estructura de Usuarios Propuesta

### **Tipos de Usuario:**

1. **ADMIN** (Tú)
   - Acceso completo al panel de administración
   - Validación por variables de entorno (actual)
   - O usuario en BD con `rol="ADMIN"`

2. **USUARIO_REGULAR** (Vendedor Individual)
   - Puede publicar vehículos
   - Panel personal
   - Gestionar sus vehículos

3. **AGENCIA** (Agencia de Autos)
   - Perfil de agencia
   - Publicar múltiples vehículos
   - Panel de administración de agencia
   - Puede tener vendedores asociados

## 🗂️ Tablas a Eliminar/Limpiar

### **Eliminar completamente:**
- ❌ `negocios` (ya no se necesitan)
- ❌ `ofertas` (reemplazadas por vehículos)
- ❌ `noticias` (opcional: mantener o eliminar)
- ❌ `resenas` (opcional: adaptar para vehículos o eliminar)
- ❌ `mensajes` (opcional: adaptar para vehículos o eliminar)
- ❌ `imagenes_negocio` (reemplazadas por `imagenes_vehiculo`)
- ❌ `favoritos` (reemplazadas por `favoritos_vehiculos`)

### **Limpiar pero mantener estructura:**
- 🧹 `usuarios` (limpiar todos excepto admin si existe)
- 🧹 `visitas` (opcional: limpiar o mantener para analytics)

### **Crear nuevas:**
- ✅ `vehiculos` (ya tenemos el modelo)
- ✅ `agencias` (ya tenemos el modelo)
- ✅ `imagenes_vehiculo` (ya tenemos el modelo)
- ✅ `favoritos_vehiculos` (ya tenemos el modelo)

## 🚀 Plan de Ejecución Recomendado

### **Fase 1: Preparación** ⚙️
1. ✅ Verificar que las credenciales admin estén en variables de entorno
2. ✅ Hacer backup de la base de datos (por seguridad)
3. ✅ Descomentar modelos de vehículos en `models.py`
4. ✅ Crear migración para nuevas tablas

### **Fase 2: Limpieza** 🧹
1. ✅ Crear script de limpieza de datos
2. ✅ Ejecutar desde panel admin o directamente
3. ✅ Verificar que admin sigue funcionando

### **Fase 3: Migración de Estructura** 📦
1. ✅ Ejecutar migración para crear tablas de vehículos
2. ✅ Agregar campos necesarios a `usuarios` (tipo_usuario, agencia_id)
3. ✅ Verificar que todo funciona

### **Fase 4: Desarrollo** 💻
1. ✅ Crear páginas de vehículos
2. ✅ Adaptar sistema de usuarios
3. ✅ Crear paneles para vendedores y agencias
4. ✅ Implementar búsqueda y filtros

### **Fase 5: Pruebas** 🧪
1. ✅ Probar publicación de vehículos
2. ✅ Probar búsqueda y filtros
3. ✅ Probar paneles de usuario y agencia
4. ✅ Verificar que admin funciona

## ⚠️ Consideraciones Importantes

### **1. Backup Antes de Limpiar**
```sql
-- Hacer backup completo de la BD antes de empezar
```

### **2. Modo Mantenimiento**
- Mantener activado durante la migración
- Solo vos podés acceder

### **3. Credenciales Admin**
- **NO se perderán** (están en variables de entorno)
- Verificar que `ADMIN_USER` y `ADMIN_PASS` estén configuradas en Render.com

### **4. Datos a Preservar (si los hay)**
- ¿Hay datos importantes que quieras conservar?
- ¿Usuarios que quieras migrar a vendedores?

## 🎨 Estructura de Roles Propuesta

```python
# En modelo Usuario:
rol = "ADMIN"        # Administrador (tú)
rol = "VENDEDOR"     # Vendedor individual
rol = "AGENCIA"      # Dueño de agencia
rol = "VENDEDOR_AGENCIA"  # Vendedor que trabaja para una agencia
```

## 📝 Checklist Antes de Empezar

- [ ] Verificar credenciales admin en Render.com (`ADMIN_USER`, `ADMIN_PASS`)
- [ ] Hacer backup de la base de datos
- [ ] Activar modo mantenimiento
- [ ] Decidir qué datos preservar (si hay)
- [ ] Revisar modelos de vehículos (ya están creados)
- [ ] Planificar estructura de usuarios

## ❓ Preguntas para Decidir

1. **¿Hay usuarios registrados que quieras conservar?**
   - Si sí: migrarlos a vendedores
   - Si no: limpiar todo

2. **¿Querés mantener noticias?**
   - Si sí: adaptarlas para vehículos
   - Si no: eliminar

3. **¿Sistema de mensajes para vehículos?**
   - Si sí: adaptar el actual
   - Si no: eliminar

4. **¿Sistema de reseñas para vehículos?**
   - Si sí: adaptar el actual
   - Si no: eliminar

## 🎯 Recomendación Final

**Usar Opción 1 (Script de Limpieza):**
- Más seguro
- Reversible
- Mantiene estructura
- Fácil de ejecutar

**Estructura de Usuarios:**
- Admin: Variables de entorno (actual) ✅
- Vendedores: Tabla usuarios con `rol="VENDEDOR"`
- Agencias: Tabla usuarios con `rol="AGENCIA"` + tabla `agencias`

¿Querés que proceda con alguna de estas opciones?
