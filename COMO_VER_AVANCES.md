# 👀 Cómo Ver los Avances de la Remodelación

## 🚀 Opción 1: Desarrollo Local (RECOMENDADO) ⭐

### Pasos Rápidos:

1. **Doble clic en `run_local.bat`** (en la carpeta del proyecto)
2. **Esperá** a que termine de instalar (solo la primera vez)
3. **Abrí tu navegador** en: `http://localhost:5000`
4. **¡Listo!** Verás todos los cambios en tiempo real

### Ventajas:
- ✅ **Ver cambios instantáneamente** (sin esperar deploy)
- ✅ **Modo mantenimiento desactivado** (podés ver todo)
- ✅ **No afecta producción**
- ✅ **Debug fácil** (errores en consola)

### Si el script no funciona:

```powershell
cd c:\Users\jperm\.cursor\flask-app
.\venv\Scripts\Activate.ps1
python main.py
```

Luego abrí: `http://localhost:5000`

## 🌐 Opción 2: Ver en Render.com (Después del Deploy)

1. **Hacé push** de los cambios (yo lo hago automáticamente)
2. **Esperá 2-5 minutos** a que Render.com despliegue
3. **Visitá tu sitio** (estará en modo mantenimiento)
4. **Iniciá sesión como admin** desde `/login`
5. **Navegá** por las nuevas páginas

## 📍 Dónde Ver Cada Parte de la Remodelación

### **Página Principal (Búsqueda de Vehículos)**
- **URL:** `http://localhost:5000/` o `/`
- **Qué verás:** Hero section, búsqueda avanzada, filtros, grid de vehículos

### **Publicar Vehículo**
- **URL:** `http://localhost:5000/vehiculos/publicar`
- **Qué verás:** Formulario paso a paso con guías en cada campo

### **Detalle de Vehículo**
- **URL:** `http://localhost:5000/vehiculo/<id>`
- **Qué verás:** Galería, información completa, botones de contacto

### **Panel de Vendedor**
- **URL:** `http://localhost:5000/panel`
- **Qué verás:** Mis vehículos, estadísticas, reseñas

### **Panel de Agencia**
- **URL:** `http://localhost:5000/panel/agencia`
- **Qué verás:** Gestión de vehículos, vendedores, noticias

## 🔄 Flujo de Trabajo Recomendado

```
1. Yo hago cambios en el código
   ↓
2. Vos corrés la app localmente (run_local.bat)
   ↓
3. Visitás http://localhost:5000
   ↓
4. Probás y me decís qué ajustar
   ↓
5. Cuando esté perfecto, hago push
   ↓
6. Render.com despliega automáticamente
```

## ⚡ Recarga Automática

Si querés que la página se recargue automáticamente al guardar cambios:

```powershell
flask run --debug --port 5000
```

Esto activa el modo debug con recarga automática.

## 🐛 Si Algo No Funciona

1. **Ver errores en la consola** donde corriste `python main.py`
2. **Verificar que el entorno virtual esté activado**
3. **Verificar que las dependencias estén instaladas:** `pip install -r requirements.txt`
4. **Verificar que la base de datos esté inicializada:** `flask db upgrade`

## 📝 Notas Importantes

- **Modo mantenimiento:** En local está **desactivado** automáticamente
- **Base de datos local:** Es independiente de producción
- **Cambios:** Solo se ven localmente hasta que hagas push
- **Render.com:** Sigue en modo mantenimiento hasta que lo desactives

## 🎯 Próximos Pasos

1. **Corré la app localmente** con `run_local.bat`
2. **Visitá** `http://localhost:5000`
3. **Probá** la nueva búsqueda de vehículos
4. **Decime** qué ajustar o mejorar
