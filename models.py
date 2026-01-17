# encoding: utf-8
"""
MODELS - Sistema de Venta de Vehículos Usados - Costa Rica
Versión simple y limpia desde cero
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timedelta

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Usuario (vendedor o admin)
class Usuario(db.Model):
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    rol = db.Column(db.String(20), default="vendedor")  # vendedor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Vehículo en venta
class Vehiculo(db.Model):
    __tablename__ = "vehiculos"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # Info básica
    marca = db.Column(db.String(50), nullable=False, index=True)
    modelo = db.Column(db.String(100), nullable=False, index=True)
    año = db.Column(db.Integer, nullable=False, index=True)
    precio = db.Column(db.Float, nullable=False, index=True)
    kilometraje = db.Column(db.Integer, index=True)
    
    # Detalles
    tipo = db.Column(db.String(50), index=True)  # Sedan, SUV, Pickup, Coupe, Van, Camion
    transmision = db.Column(db.String(20), index=True)  # Manual, Automatica
    combustible = db.Column(db.String(30), index=True)  # Gasolina, Diesel, Electrico, Hibrido
    color = db.Column(db.String(50))
    descripcion = db.Column(db.Text, nullable=False)
    
    # Ubicación
    provincia = db.Column(db.String(50), index=True)
    canton = db.Column(db.String(100))
    
    # Contacto
    telefono = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    
    # Imagen
    imagen_url = db.Column(db.String(500))
    
    # Estado
    estado = db.Column(db.String(20), default="pendiente", index=True)  # pendiente, aprobado, vendido
    es_vip = db.Column(db.Boolean, default=False, index=True)
    destacado = db.Column(db.Boolean, default=False, index=True)
    
    # Fechas
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, index=True)  # Vence en 3 meses
    
    # Índices compuestos para búsquedas rápidas (optimización para miles de usuarios)
    __table_args__ = (
        db.Index('ix_vehiculos_estado_vip', 'estado', 'es_vip'),
        db.Index('ix_vehiculos_marca_modelo', 'marca', 'modelo'),
        db.Index('ix_vehiculos_precio_año', 'precio', 'año'),
        db.Index('ix_vehiculos_provincia_estado', 'provincia', 'estado'),
    )

# Agencia de vehículos
class Agencia(db.Model):
    __tablename__ = "agencias"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(200))
    provincia = db.Column(db.String(50))
    estado = db.Column(db.String(20), default="pendiente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
