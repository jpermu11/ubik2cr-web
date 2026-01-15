# 🚗 Plan de Diseño: Plataforma de Venta de Vehículos Usados

## 🎨 Identidad Visual

### Colores del Logo
- **Azul Principal:** `#0b4fa3` (Brand Blue)
- **Verde Complementario:** `#38b24d` (Brand Green)
- **Grises:** Para textos y fondos neutros
- **Blancos:** Para contraste y limpieza

### Principios de Diseño
- ✅ **Profesional y Moderno**
- ✅ **Atractivo visualmente**
- ✅ **Interactivo y dinámico**
- ✅ **Fácil de usar (UX intuitiva)**
- ✅ **Responsive (móvil y desktop)**
- ✅ **Guías claras en cada campo**

## 🔍 Sistema de Búsqueda Avanzada (Estilo Crautos)

### Filtros Principales
1. **Marca** (dropdown con búsqueda)
2. **Modelo** (dinámico según marca)
3. **Año** (rango: desde - hasta)
4. **Precio** (rango: mínimo - máximo)
5. **Kilometraje** (rango: mínimo - máximo)
6. **Tipo de Vehículo** (Sedán, SUV, Pickup, Moto, etc.)
7. **Transmisión** (Manual, Automática)
8. **Combustible** (Gasolina, Diésel, Eléctrico, Híbrido)
9. **Provincia** (dropdown)
10. **Cantón** (dinámico según provincia)
11. **Estado** (Nuevo, Usado, Seminuevo)

### Opciones de Ordenamiento
- 📅 **Más recientes primero** (default)
- 📅 **Más antiguos primero**
- 💰 **Precio: menor a mayor**
- 💰 **Precio: mayor a menor**
- 🏁 **Kilometraje: menor a mayor**
- 🏁 **Kilometraje: mayor a menor**
- ⭐ **Mejor calificados primero** (vendedor/agencia)
- 🔥 **Destacados/VIP primero**

### Características de Búsqueda
- Búsqueda por texto libre (marca, modelo, descripción)
- Filtros combinables
- Guardar búsquedas favoritas
- Comparar vehículos (hasta 3)
- Vista de lista y vista de tarjetas

## 💎 Sistema VIP/Destacado

### Características VIP
- ⭐ **Badge "Destacado"** visible en todas las búsquedas
- 🎯 **Aparece primero** en resultados (antes que publicaciones normales)
- 🔝 **Posición fija** en top de listados
- 📸 **Más fotos permitidas** (hasta 20 vs 10 normales)
- 🎨 **Diseño especial** en tarjetas
- 📊 **Estadísticas avanzadas** (vistas, contactos)
- ⏰ **Duración:** 30 días (renovable)

### Precios Sugeridos
- **Publicación Normal:** Gratis
- **Publicación VIP:** ₡15,000 - ₡25,000 (30 días)
- **Membresía Agencia:** ₡50,000 - ₡100,000 (mensual)

## 📝 Guías y Ayuda en Formularios

### Cada Campo Incluirá:
- **Label claro** con icono
- **Placeholder** con ejemplo
- **Tooltip** con información adicional
- **Validación en tiempo real**
- **Mensajes de error claros**
- **Ejemplos visuales** cuando sea necesario

### Ejemplos:
- **Marca:** "Ej: Toyota, Honda, Nissan"
- **Precio:** "Ingresá el precio en colones (ej: 5000000)"
- **Kilometraje:** "Kilómetros recorridos (ej: 50000)"
- **Descripción:** "Contá detalles importantes del vehículo..."

## 🎯 Estructura de Páginas

### 1. Página Principal (Búsqueda)
- Hero section con búsqueda rápida
- Filtros avanzados (colapsable)
- Grid de vehículos destacados
- Categorías populares
- CTA para publicar

### 2. Detalle de Vehículo
- Galería de imágenes (lightbox)
- Información completa
- Mapa de ubicación
- Botones de contacto (WhatsApp, Email)
- Reseñas del vendedor/agencia
- Vehículos similares
- Compartir en redes sociales

### 3. Publicar Vehículo
- Formulario paso a paso (wizard)
- Validación en cada paso
- Vista previa antes de publicar
- Guías contextuales

### 4. Panel de Vendedor
- Mis vehículos publicados
- Estadísticas (vistas, contactos)
- Mensajes recibidos
- Reseñas recibidas
- Opción de hacer VIP

### 5. Panel de Agencia
- Gestión de vehículos
- Gestión de vendedores
- Estadísticas generales
- Noticias de la agencia
- Reseñas de la agencia

## 🔔 Sistema de Notificaciones

### Email/WhatsApp (No guardar en BD)
- Notificación al vendedor cuando alguien contacta
- Recordatorio de publicación próxima a vencer
- Confirmación de publicación aprobada
- Notificación de nueva reseña

## ⭐ Sistema de Reseñas

### Para Vendedores/Agencias
- Calificación 1-5 estrellas
- Comentario opcional
- Verificación de compra (opcional)
- Respuesta del vendedor/agencia
- Filtro por calificación en búsqueda

## 📱 Responsive Design

- **Mobile First:** Diseño pensado primero para móvil
- **Breakpoints:** 320px, 768px, 1024px, 1440px
- **Touch Friendly:** Botones grandes, fácil de tocar
- **Carga rápida:** Imágenes optimizadas, lazy loading

## 🎨 Componentes de Diseño

### Tarjetas de Vehículo
- Imagen principal destacada
- Badge VIP si aplica
- Precio grande y visible
- Información clave (año, km, tipo)
- Botón de contacto rápido
- Hover effects suaves

### Botones
- Primarios: Azul (#0b4fa3)
- Secundarios: Verde (#38b24d)
- Acciones: Gradientes
- Hover: Transform y shadow

### Tipografía
- Títulos: Bold, grande
- Texto: Legible, tamaño adecuado
- Jerarquía clara

## 🚀 Próximos Pasos

1. Crear script de limpieza ✅
2. Adaptar modelos (Noticia, Resena)
3. Crear sistema de búsqueda avanzada
4. Diseñar componentes UI
5. Implementar sistema VIP
6. Crear formularios con guías
7. Adaptar paneles
