# encoding: utf-8
"""Crear base de datos y usuario admin"""
from main import app
from models import db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    print("Recreando base de datos...")
    db.drop_all()
    db.create_all()
    
    # Crear admin
    admin = Usuario(
        email="info@ubik2cr.com",
        password=generate_password_hash("UjifamKJ252319@"),
        nombre="Admin",
        rol="admin"
    )
    db.session.add(admin)
    db.session.commit()
    
    print("OK - Base de datos creada")
    print("Admin: info@ubik2cr.com / UjifamKJ252319@")
