#!/usr/bin/env python
"""
Script para crear el usuario administrador inicial
Ejecutar: python crear_admin.py
"""
import os
from werkzeug.security import generate_password_hash

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

from main import app
from models import db, Usuario

def crear_admin():
    """Crear usuario administrador"""
    with app.app_context():
        # Verificar si ya existe un admin
        admin_existente = Usuario.query.filter_by(rol="admin").first()
        
        if admin_existente:
            print(f"⚠️  Ya existe un usuario admin: {admin_existente.email}")
            respuesta = input("¿Deseas crear otro admin? (s/n): ")
            if respuesta.lower() != 's':
                return
        
        # Obtener credenciales de variables de entorno o usar valores por defecto
        admin_email = os.environ.get("ADMIN_USER", "info@ubik2cr.com")
        admin_pass = os.environ.get("ADMIN_PASS", "UjifamKJ252319@")
        
        # Crear usuario admin
        nuevo_admin = Usuario(
            email=admin_email,
            password=generate_password_hash(admin_pass),
            nombre="Administrador",
            rol="admin"
        )
        
        try:
            db.session.add(nuevo_admin)
            db.session.commit()
            print(f"✅ Usuario admin creado exitosamente!")
            print(f"   Email: {admin_email}")
            print(f"   Contraseña: {admin_pass}")
            print(f"\n🔗 Puedes iniciar sesión en: http://localhost:5000/login")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear admin: {e}")

if __name__ == "__main__":
    crear_admin()
