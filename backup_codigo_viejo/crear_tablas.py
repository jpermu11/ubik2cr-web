#!/usr/bin/env python
"""
Script para crear todas las tablas directamente sin migraciones
"""
from main import app
from models import db

print("Creando todas las tablas...")

with app.app_context():
    # Eliminar y crear todas las tablas desde cero
    print("Eliminando tablas antiguas...")
    db.drop_all()
    
    print("Creando tablas nuevas...")
    db.create_all()
    
    # Verificar que las tablas existan
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tablas = inspector.get_table_names()
    print(f"Tablas creadas: {', '.join(tablas)}")
    print("OK - Base de datos lista")

print("Listo! Ejecuta: python main.py")
