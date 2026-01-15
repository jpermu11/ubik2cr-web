# Plan de Migración: Ubik2CR → Plataforma de Venta de Vehículos

## Objetivo
Convertir Ubik2CR en una plataforma estilo Crautos para la venta de vehículos usados en Costa Rica.

## Estructura Propuesta

### 1. Modelos de Base de Datos

#### Modelo `Vehiculo` (Nuevo)
- id, owner_id (vendedor)
- marca, modelo, año
- precio, kilometraje
- tipo_vehiculo (sedán, SUV, pickup, moto, etc.)
- transmision (manual, automática)
- combustible (gasolina, diésel, eléctrico, híbrido)
- color, estado (nuevo, usado, seminuevo)
- descripcion, provincia, canton, distrito
- telefono, whatsapp
- imagenes (múltiples)
- estado_publicacion (pendiente, aprobado, vendido)
- es_vip, destacado
- created_at, updated_at

#### Modelo `Agencia` (Nuevo)
- id, owner_id
- nombre, descripcion
- telefono, whatsapp, email
- ubicacion, provincia, canton
- logo_url, imagen_url
- estado (pendiente, aprobado)
- vehiculos (relación con Vehiculo)

#### Adaptación de `Usuario`
- Agregar campo `tipo_usuario`: "individual", "agencia"
- Agregar campo `agencia_id` (si es vendedor de agencia)

### 2. Funcionalidades Principales

#### Para Vendedores Individuales:
- Publicar vehículo (con múltiples fotos)
- Editar/eliminar sus vehículos
- Ver mensajes de interesados
- Panel de control personal

#### Para Agencias:
- Crear perfil de agencia
- Publicar múltiples vehículos agrupados
- Panel de administración de vehículos
- Estadísticas de visualizaciones

#### Para Compradores:
- Buscar vehículos por múltiples filtros
- Ver detalles completos
- Contactar vendedor/agencia
- Guardar favoritos
- Comparar vehículos

### 3. Filtros de Búsqueda
- Marca, Modelo, Año (rango)
- Precio (rango)
- Kilometraje (rango)
- Tipo de vehículo
- Transmisión, Combustible
- Provincia, Cantón
- Estado (nuevo/usado)

### 4. Sistema de Ingresos
- Publicación básica: Gratis
- Publicación VIP: Con costo (destacado)
- Membresía de agencia: Plan mensual/anual

## Ventajas de Reutilizar la Infraestructura Actual

✅ Sistema de usuarios y autenticación
✅ Sistema de imágenes (Cloudinary)
✅ Sistema de mensajes
✅ Sistema de favoritos
✅ Panel de administración
✅ Sistema de aprobación/moderation
✅ Analytics básico
✅ Ubicación geográfica (provincia/cantón/distrito)

## Archivos a Crear/Modificar

### Nuevos:
- `models.py`: Agregar Vehiculo y Agencia
- `migrations/`: Nueva migración
- `templates/vehiculos/`: Carpeta con templates
  - `index.html` (búsqueda)
  - `publicar.html` (formulario)
  - `detalle.html` (detalle del vehículo)
  - `panel_vehiculos.html` (panel vendedor)

### Modificar:
- `main.py`: Nuevas rutas para vehículos
- `index.html`: Cambiar a búsqueda de vehículos
- `dashboard.html`: Adaptar opciones

## Fases de Implementación

### Fase 1: Base de Datos y Modelos
- Crear modelos Vehiculo y Agencia
- Migración de base de datos

### Fase 2: Publicación
- Formulario de publicación
- Subida de múltiples imágenes
- Guardado en base de datos

### Fase 3: Búsqueda y Listado
- Página principal con búsqueda
- Filtros avanzados
- Paginación

### Fase 4: Detalles y Contacto
- Página de detalle
- Sistema de contacto
- Favoritos

### Fase 5: Paneles
- Panel de vendedor
- Panel de agencia
- Panel de administración
