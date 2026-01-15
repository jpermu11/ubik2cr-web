from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import hashlib

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# --- MODELO USUARIO ---
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)

    # ✅ IMPORTANTE: 255 para hashes (scrypt/pbkdf2)
    password = db.Column(db.String(255), nullable=False)

    nombre = db.Column(db.String(100))
    rol = db.Column(db.String(20), default="VENDEDOR", index=True)  # ADMIN, VENDEDOR, AGENCIA, VENDEDOR_AGENCIA
    
    # Campos para sistema de vehículos (TEMPORALMENTE DESHABILITADO)
    tipo_usuario = db.Column(db.String(20), default="individual", index=True)  # individual, agencia
    # agencia_id = db.Column(db.Integer, db.ForeignKey("agencias.id"), nullable=True, index=True)  # TEMPORALMENTE COMENTADO

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    negocios = db.relationship("Negocio", backref="owner", lazy=True)
    # vehiculos = db.relationship("Vehiculo", foreign_keys="Vehiculo.owner_id", backref="vendedor", lazy=True)  # TEMPORALMENTE COMENTADO

# --- MODELO NEGOCIO ---
class Negocio(db.Model):
    __tablename__ = "negocios"

    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)

    nombre = db.Column(db.String(100), nullable=False, index=True)
    categoria = db.Column(db.String(50), nullable=False, index=True)
    estado = db.Column(db.String(20), default="pendiente", index=True)  # pendiente, aprobado

    ubicacion = db.Column(db.String(200), nullable=False)
    
    # Ubicación geográfica de Costa Rica
    provincia = db.Column(db.String(50), nullable=True, index=True)
    canton = db.Column(db.String(100), nullable=True, index=True)
    distrito = db.Column(db.String(100), nullable=True, index=True)

    latitud = db.Column(db.Float, nullable=True, index=True)
    longitud = db.Column(db.Float, nullable=True, index=True)
    maps_url = db.Column(db.String(500), nullable=True)

    telefono = db.Column(db.String(20), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    # Horario (simple): texto libre + flag 24h
    horario = db.Column(db.String(300), nullable=True)
    abierto_24h = db.Column(db.Boolean, default=False, index=True)
    descripcion = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(500), nullable=True)
    
    # Tags/Productos personalizados que vende el negocio (como hashtags)
    # Almacenado como JSON: ["martillo", "clavos", "pintura", "herramientas"]
    productos_tags = db.Column(db.Text, nullable=True)  # JSON string con lista de productos/tags

    es_vip = db.Column(db.Boolean, default=False, index=True)
    calificacion = db.Column(db.Float, default=0.0)
    total_votos = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        db.Index("ix_negocios_estado_categoria", "estado", "categoria"),
        db.Index("ix_negocios_estado_id", "estado", "id"),
        db.Index("ix_negocios_provincia_canton", "provincia", "canton"),
        db.Index("ix_negocios_provincia_canton_distrito", "provincia", "canton", "distrito"),
    )

# --- MODELO NOTICIA (Adaptado para Agencias de Autos) ---
class Noticia(db.Model):
    __tablename__ = "noticias"

    id = db.Column(db.Integer, primary_key=True)
    # Ahora las noticias son de agencias (no de negocios)
    # agencia_id = db.Column(db.Integer, db.ForeignKey("agencias.id"), nullable=True, index=True)  # TEMPORALMENTE COMENTADO
    # Mantener negocio_id por compatibilidad durante migración, pero será NULL
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id"), nullable=True, index=True)  # DEPRECATED - mantener por compatibilidad
    
    titulo = db.Column(db.String(200), nullable=False, index=True)
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(500))
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_caducidad = db.Column(db.DateTime, nullable=False, index=True)  # OBLIGATORIA - Fecha de desaparición automática
    
    # Relaciones
    # negocio = db.relationship("Negocio", backref="noticias")  # DEPRECATED
    # agencia = db.relationship("Agencia", backref="noticias")  # TEMPORALMENTE COMENTADO

# --- MODELO FAVORITOS (relación muchos-a-muchos) ---
favoritos = db.Table(
    'favoritos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('negocio_id', db.Integer, db.ForeignKey('negocios.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# --- MODELO RESEÑA (Adaptado para Vendedores/Agencias) ---
class Resena(db.Model):
    __tablename__ = "resenas"

    id = db.Column(db.Integer, primary_key=True)
    
    # Reseña para vendedor individual o agencia (NO para vehículos)
    vendedor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)  # Vendedor individual
    # agencia_id = db.Column(db.Integer, db.ForeignKey("agencias.id"), nullable=True, index=True)  # TEMPORALMENTE COMENTADO
    
    # Mantener negocio_id por compatibilidad durante migración
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id"), nullable=True, index=True)  # DEPRECATED
    
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)  # Usuario que hace la reseña
    
    nombre_usuario = db.Column(db.String(100))  # Para reseñas anónimas
    email_usuario = db.Column(db.String(180))  # Para reseñas anónimas
    
    calificacion = db.Column(db.Integer, nullable=False)  # 1-5 estrellas
    comentario = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default="aprobado", index=True)  # aprobado, pendiente, rechazado
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    # negocio = db.relationship("Negocio", backref="resenas")  # DEPRECATED
    vendedor = db.relationship("Usuario", foreign_keys=[vendedor_id], backref="resenas_recibidas")
    # agencia = db.relationship("Agencia", backref="resenas")  # TEMPORALMENTE COMENTADO
    usuario = db.relationship("Usuario", foreign_keys=[usuario_id], backref="resenas_enviadas")

# --- MODELO IMAGEN DE NEGOCIO ---
class ImagenNegocio(db.Model):
    __tablename__ = "imagenes_negocio"
    
    id = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id"), nullable=False, index=True)
    imagen_url = db.Column(db.String(500), nullable=False)
    orden = db.Column(db.Integer, default=0, index=True)  # Para ordenar las imágenes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    negocio = db.relationship("Negocio", backref="imagenes")

# --- MODELO OFERTA ---
class Oferta(db.Model):
    __tablename__ = "ofertas"

    id = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id"), nullable=False, index=True)
    
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(500), nullable=False)
    
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_caducidad = db.Column(db.DateTime, nullable=False, index=True)
    
    estado = db.Column(db.String(20), default="activa", index=True)  # activa, expirada
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relación
    negocio = db.relationship("Negocio", backref="ofertas")
    
    __table_args__ = (
        db.Index("ix_ofertas_negocio_fecha", "negocio_id", "fecha_caducidad"),
        db.Index("ix_ofertas_estado_fecha", "estado", "fecha_caducidad"),
    )

# --- MODELO MENSAJE ---
class Mensaje(db.Model):
    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)  # Usuario registrado (opcional)
    
    # Para usuarios anónimos
    nombre_remitente = db.Column(db.String(100), nullable=False)
    email_remitente = db.Column(db.String(180), nullable=False, index=True)
    
    asunto = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    
    leido = db.Column(db.Boolean, default=False, index=True)
    respondido = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    negocio = db.relationship("Negocio", backref="mensajes")
    usuario = db.relationship("Usuario", backref="mensajes_enviados")
    
    __table_args__ = (
        db.Index("ix_mensajes_negocio_leido", "negocio_id", "leido"),
        db.Index("ix_mensajes_negocio_fecha", "negocio_id", "created_at"),
    )

# --- MODELO VISITA (Analytics) ---
class Visita(db.Model):
    __tablename__ = "visitas"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # IP hasheada para privacidad (últimos 8 caracteres del hash SHA256)
    ip_hash = db.Column(db.String(64), nullable=False, index=True)
    
    # URL visitada (relativa, sin dominio)
    url = db.Column(db.String(500), nullable=False, index=True)
    
    # User Agent básico (solo navegador/plataforma)
    user_agent = db.Column(db.String(200), nullable=True)
    
    # Referrer (de dónde vino)
    referrer = db.Column(db.String(500), nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index("ix_visitas_fecha", "created_at"),
        db.Index("ix_visitas_url_fecha", "url", "created_at"),
    )

# --- MODELO AGENCIA (Para agencias de autos) ---
class Agencia(db.Model):
    __tablename__ = "agencias"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    
    nombre = db.Column(db.String(100), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    
    telefono = db.Column(db.String(20), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(180), nullable=True)
    
    ubicacion = db.Column(db.String(200), nullable=True)
    provincia = db.Column(db.String(50), nullable=True, index=True)
    canton = db.Column(db.String(100), nullable=True, index=True)
    distrito = db.Column(db.String(100), nullable=True, index=True)
    
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    
    logo_url = db.Column(db.String(500), nullable=True)
    imagen_url = db.Column(db.String(500), nullable=True)
    
    estado = db.Column(db.String(20), default="pendiente", index=True)  # pendiente, aprobado
    es_vip = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    owner = db.relationship("Usuario", backref="agencia_owned")
    vehiculos = db.relationship("Vehiculo", backref="agencia", lazy=True)
    
    __table_args__ = (
        db.Index("ix_agencias_estado", "estado"),
        db.Index("ix_agencias_provincia", "provincia"),
    )
"""

# --- MODELO VEHICULO --- (TEMPORALMENTE DESHABILITADO)
"""
class Vehiculo(db.Model):
    __tablename__ = "vehiculos"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Vendedor (puede ser individual o agencia)
    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    agencia_id = db.Column(db.Integer, db.ForeignKey("agencias.id"), nullable=True, index=True)  # Si pertenece a una agencia
    
    # Información básica
    marca = db.Column(db.String(50), nullable=False, index=True)
    modelo = db.Column(db.String(100), nullable=False, index=True)
    año = db.Column(db.Integer, nullable=False, index=True)
    
    # Precio y características
    precio = db.Column(db.Numeric(12, 2), nullable=False, index=True)  # Precio en colones
    kilometraje = db.Column(db.Integer, nullable=True, index=True)  # En kilómetros
    
    # Tipo y especificaciones
    tipo_vehiculo = db.Column(db.String(50), nullable=False, index=True)  # Sedán, SUV, Pickup, Moto, etc.
    transmision = db.Column(db.String(20), nullable=True, index=True)  # Manual, Automática
    combustible = db.Column(db.String(30), nullable=True, index=True)  # Gasolina, Diésel, Eléctrico, Híbrido
    color = db.Column(db.String(50), nullable=True)
    estado_vehiculo = db.Column(db.String(20), default="usado", index=True)  # Nuevo, Usado, Seminuevo
    
    # Descripción y ubicación
    descripcion = db.Column(db.Text, nullable=False)
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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    fecha_venta = db.Column(db.DateTime, nullable=True)  # Cuando se marca como vendido
    
    __table_args__ = (
        db.Index("ix_vehiculos_marca_modelo", "marca", "modelo"),
        db.Index("ix_vehiculos_estado_precio", "estado", "precio"),
        db.Index("ix_vehiculos_año_precio", "año", "precio"),
        db.Index("ix_vehiculos_tipo_estado", "tipo_vehiculo", "estado"),
        db.Index("ix_vehiculos_provincia_estado", "provincia", "estado"),
    )
"""

# --- MODELO IMAGEN DE VEHICULO --- (TEMPORALMENTE DESHABILITADO)
"""
class ImagenVehiculo(db.Model):
    __tablename__ = "imagenes_vehiculo"
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"), nullable=False, index=True)
    imagen_url = db.Column(db.String(500), nullable=False)
    orden = db.Column(db.Integer, default=0, index=True)  # Para ordenar las imágenes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relación
    vehiculo = db.relationship("Vehiculo", backref="imagenes")
"""

# --- TABLA FAVORITOS VEHICULOS (relación muchos-a-muchos) --- (TEMPORALMENTE DESHABILITADO)
"""
favoritos_vehiculos = db.Table(
    'favoritos_vehiculos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('vehiculo_id', db.Integer, db.ForeignKey('vehiculos.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
"""
