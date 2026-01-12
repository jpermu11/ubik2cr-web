#!/usr/bin/env python
"""
Script de prueba rápida para verificar que todo esté configurado correctamente
"""
import sys
import os

print("=" * 50)
print("🧪 PRUEBA RÁPIDA - Ubik2CR")
print("=" * 50)

# 1. Verificar Python
print("\n1. Verificando versión de Python...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 8):
    print("   ⚠️  ADVERTENCIA: Se recomienda Python 3.8 o superior")
else:
    print("   ✅ Versión de Python OK")

# 2. Verificar dependencias
print("\n2. Verificando dependencias...")
try:
    import flask
    print(f"   ✅ Flask {flask.__version__}")
except ImportError:
    print("   ❌ Flask no instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

try:
    import flask_sqlalchemy
    print("   ✅ Flask-SQLAlchemy instalado")
except ImportError:
    print("   ❌ Flask-SQLAlchemy no instalado")
    sys.exit(1)

try:
    import flask_migrate
    print("   ✅ Flask-Migrate instalado")
except ImportError:
    print("   ❌ Flask-Migrate no instalado")
    sys.exit(1)

# 3. Verificar estructura de archivos
print("\n3. Verificando estructura de archivos...")
files_needed = [
    "main.py",
    "models.py",
    "requirements.txt",
    "templates/index.html",
    "static/uploads"
]

all_ok = True
for file in files_needed:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - NO ENCONTRADO")
        all_ok = False

# 4. Verificar configuración de base de datos
print("\n4. Verificando configuración de base de datos...")
database_url = os.environ.get("DATABASE_URL", "").strip()
if not database_url:
    print("   ℹ️  DATABASE_URL no configurado - usará SQLite (app.db)")
    print("   ✅ Configuración OK para desarrollo")
else:
    print(f"   ✅ DATABASE_URL configurado: {database_url[:30]}...")

# 5. Intentar importar la aplicación
print("\n5. Verificando que la aplicación se puede importar...")
try:
    # Cambiar al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Intentar importar (sin ejecutar)
    sys.path.insert(0, os.getcwd())
    from models import db, Negocio, Usuario, Noticia
    print("   ✅ Modelos importados correctamente")
except Exception as e:
    print(f"   ❌ Error al importar modelos: {e}")
    all_ok = False

# Resumen
print("\n" + "=" * 50)
if all_ok:
    print("✅ TODO PARECE ESTAR BIEN")
    print("\nPróximos pasos:")
    print("1. flask db init")
    print("2. flask db migrate -m 'Initial migration'")
    print("3. flask db upgrade")
    print("4. python main.py")
else:
    print("⚠️  HAY ALGUNOS PROBLEMAS - Revisa los errores arriba")
print("=" * 50)

