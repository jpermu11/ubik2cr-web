"""
MODELS.PY - SOLO PARA VENTA DE VEHÍCULOS USADOS
Sistema para vendedores individuales y agencias de autos en Costa Rica
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timedelta

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# =====================================================
# MODELO USUARIO (Vendedores individuales y de agencias)
# =====================================================
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # Hash de contraseña
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    
    rol = db.Column(db.String(20), default="vendedor", index=True)  # admin, vendedor, agencia
    tipo_usuario = db.Column(db.String(20), default="individual", index=True)  # individual, agencia
    agencia_id = db.Column(db.Integer, db.ForeignKey("agencias.id"), nullable=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    vehiculos = db.relationship("Vehiculo", foreign_keys="Vehiculo.owner_id", backref="vendedor", lazy=True)
    agencia = db.relationship("Agencia", foreign_keys=[agencia_id], backref="empleados")

# =====================================================
# MODELO AGENCIA (Agencias de vehículos)
# =====================================================
class Agencia(db.Model):
    __tablename__ = "agencias"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    
    nombre = db.Column(db.String(100), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    
    # Contacto
    telefono = db.Column(db.String(20), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(180), nullable=True)
    
    # Ubicación
    ubicacion = db.Column(db.String(200), nullable=True)
    provincia = db.Column(db.String(50), nullable=True, index=True)
    canton = db.Column(db.String(100), nullable=True, index=True)
    distrito = db.Column(db.String(100), nullable=True, index=True)
    
    # Imágenes
    logo_url = db.Column(db.String(500), nullable=True)
    imagen_url = db.Column(db.String(500), nullable=True)
    
    # Estado y destacado
    estado = db.Column(db.String(20), default="pendiente", index=True)  # pendiente, aprobado, rechazado
    es_vip = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    owner = db.relationship("Usuario", foreign_keys=[owner_id], backref="agencia_propietario")
    vehiculos = db.relationship("Vehiculo", foreign_keys="Vehiculo.agencia_id", backref="agencia_relacionada", lazy=True)

# =====================================================
# MODELO VEHICULO (Publicaciones de vehículos)
# =====================================================
class Vehiculo(db.Model):
    __tablename__ = "vehiculos"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Vendedor (individual o de agencia)
    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    agencia_id = db.Column(db.Integer, db.ForeignKey("agencias.id"), nullable=True, index=True)
    
    # Información del vehículo
    marca = db.Column(db.String(50), nullable=False, index=True)
    modelo = db.Column(db.String(100), nullable=False, index=True)
    año = db.Column(db.Integer, nullable=False, index=True)
    
    # Precio y kilometraje
    precio = db.Column(db.Numeric(12, 2), nullable=False, index=True)
    kilometraje = db.Column(db.Integer, nullable=True, index=True)
    
    # Especificaciones
    tipo_vehiculo = db.Column(db.String(50), nullable=False, index=True)  # Sedán, SUV, Pickup, etc.
    transmision = db.Column(db.String(20), nullable=True, index=True)  # Manual, Automática
    combustible = db.Column(db.String(30), nullable=True, index=True)  # Gasolina, Diésel, Eléctrico
    color = db.Column(db.String(50), nullable=True)
    estado_vehiculo = db.Column(db.String(20), default="usado", index=True)  # Nuevo, Usado, Seminuevo
    
    # Descripción
    descripcion = db.Column(db.Text, nullable=False)
    
    # Ubicación
    provincia = db.Column(db.String(50), nullable=True, index=True)
    canton = db.Column(db.String(100), nullable=True, index=True)
    distrito = db.Column(db.String(100), nullable=True, index=True)
    
    # Contacto
    telefono = db.Column(db.String(20), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    
    # Imagen principal
    imagen_url = db.Column(db.String(500), nullable=True)
    
    # Estado de publicación
    estado = db.Column(db.String(20), default="pendiente", index=True)  # pendiente, aprobado, vendido, eliminado
    es_vip = db.Column(db.Boolean, default=False, index=True)
    destacado = db.Column(db.Boolean, default=False, index=True)
    
    # Fechas
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_venta = db.Column(db.DateTime, nullable=True)
    
    # Sistema de vencimiento automático (3 meses)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True, index=True)
    notificacion_vencimiento_enviada = db.Column(db.Boolean, default=False, index=True)
    
    __table_args__ = (
        db.Index("ix_vehiculos_marca_modelo", "marca", "modelo"),
        db.Index("ix_vehiculos_estado_precio", "estado", "precio"),
        db.Index("ix_vehiculos_provincia_estado", "provincia", "estado"),
    )

# =====================================================
# MODELO IMAGEN VEHICULO (Galería de fotos)
# =====================================================
class ImagenVehiculo(db.Model):
    __tablename__ = "imagenes_vehiculo"
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"), nullable=False, index=True)
    imagen_url = db.Column(db.String(500), nullable=False)
    orden = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    vehiculo = db.relationship("Vehiculo", backref="imagenes")

# =====================================================
# MODELO RESEÑA (Para vendedores y agencias)
# =====================================================
class Resena(db.Model):
    __tablename__ = "resenas"

    id = db.Column(db.Integer, primary_key=True)
    
    # Reseña para vendedor individual o agencia
    vendedor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)
    agencia_id = db.Column(db.Integer, db.ForeignKey("agencias.id"), nullable=True, index=True)
    
    # Usuario que hace la reseña
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)
    nombre_usuario = db.Column(db.String(100), nullable=True)
    email_usuario = db.Column(db.String(180), nullable=True)
    
    # Contenido
    calificacion = db.Column(db.Integer, nullable=False)  # 1-5 estrellas
    comentario = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default="aprobado", index=True)  # aprobado, pendiente, rechazado
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    vendedor = db.relationship("Usuario", foreign_keys=[vendedor_id], backref="resenas_recibidas")
    agencia = db.relationship("Agencia", backref="resenas")
    usuario = db.relationship("Usuario", foreign_keys=[usuario_id], backref="resenas_enviadas")

# =====================================================
# FAVORITOS DE VEHÍCULOS (Tabla de relación)
# =====================================================
favoritos_vehiculos = db.Table(
    'favoritos_vehiculos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('vehiculo_id', db.Integer, db.ForeignKey('vehiculos.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# =====================================================
# MODELO VISITA (Analytics)
# =====================================================
class Visita(db.Model):
    __tablename__ = "visitas"
    
    id = db.Column(db.Integer, primary_key=True)
    ip_hash = db.Column(db.String(64), nullable=False, index=True)
    url = db.Column(db.String(500), nullable=False, index=True)
    user_agent = db.Column(db.String(200), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
