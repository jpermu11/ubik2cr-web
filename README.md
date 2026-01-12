# Ubik2CR - Tu cantón en tu mano

Aplicación web Flask para gestionar un directorio de negocios y lugares de un cantón en Costa Rica.

## 🚀 Características

- **Público**: Búsqueda de negocios, vista en mapa, noticias
- **Dueños**: Registro, panel de gestión, publicación de negocios
- **Admin**: Aprobación de negocios, gestión VIP, edición

## 📋 Requisitos

- Python 3.8+
- PostgreSQL (producción) o SQLite (desarrollo)

## 🔧 Instalación

1. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:
   - Crea un archivo `.env` o configura las variables de entorno:
   - `DATABASE_URL` - URL de la base de datos (o usa SQLite por defecto)
   - `SESSION_SECRET` - Clave secreta para sesiones
   - `ADMIN_USER` - Usuario administrador
   - `ADMIN_PASS` - Contraseña administrador
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` - Para emails

4. **Inicializar base de datos**:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. **Ejecutar la aplicación**:
```bash
python main.py
# O: flask run
```

La aplicación estará disponible en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
flask-app/
├── main.py              # Aplicación principal Flask
├── models.py            # Modelos de base de datos
├── requirements.txt     # Dependencias Python
├── templates/          # Templates HTML
├── static/             # Archivos estáticos (CSS, imágenes)
│   ├── css/
│   └── uploads/        # Imágenes subidas
└── migrations/         # Migraciones de base de datos
```

## 🔐 Variables de Entorno

Para desarrollo local, puedes usar SQLite (no necesitas configurar DATABASE_URL).

Para producción, configura:
- `DATABASE_URL=postgresql://usuario:password@host:puerto/database?sslmode=require`
- `SESSION_SECRET=tu-clave-secreta-super-segura`
- `ADMIN_USER=admin`
- `ADMIN_PASS=tu-password`
- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_USER=tu-email@gmail.com`
- `SMTP_PASS=tu-app-password`

## 📝 Notas

- Si no configuras `DATABASE_URL`, usará SQLite local (`app.db`)
- Las imágenes se guardan en `static/uploads/`
- Necesitas un logo en `static/uploads/logo.png` (o se usará placeholder)

## 🐛 Solución de Problemas

- **Error de base de datos**: Verifica que `DATABASE_URL` esté correcto o deja vacío para SQLite
- **Error de migraciones**: Ejecuta `flask db upgrade` después de `flask db migrate`
- **Imágenes no se ven**: Verifica que la carpeta `static/uploads/` exista y tenga permisos

