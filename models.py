from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

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
    rol = db.Column(db.String(20), default="OWNER", index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    negocios = db.relationship("Negocio", backref="owner", lazy=True)

# --- MODELO NEGOCIO ---
class Negocio(db.Model):
    __tablename__ = "negocios"

    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)

    nombre = db.Column(db.String(100), nullable=False, index=True)
    categoria = db.Column(db.String(50), nullable=False, index=True)
    estado = db.Column(db.String(20), default="pendiente", index=True)  # pendiente, aprobado

    ubicacion = db.Column(db.String(200), nullable=False)

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
    )

# --- MODELO NOTICIA ---
class Noticia(db.Model):
    __tablename__ = "noticias"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False, index=True)
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(500))
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_caducidad = db.Column(db.DateTime, nullable=True, index=True)  # Fecha de desaparición automática

# --- MODELO FAVORITOS (relación muchos-a-muchos) ---
favoritos = db.Table(
    'favoritos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('negocio_id', db.Integer, db.ForeignKey('negocios.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# --- MODELO RESEÑA ---
class Resena(db.Model):
    __tablename__ = "resenas"

    id = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(db.Integer, db.ForeignKey("negocios.id"), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True, index=True)
    
    nombre_usuario = db.Column(db.String(100))  # Para reseñas anónimas
    email_usuario = db.Column(db.String(180))  # Para reseñas anónimas
    
    calificacion = db.Column(db.Integer, nullable=False)  # 1-5 estrellas
    comentario = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default="aprobado", index=True)  # aprobado, pendiente, rechazado
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    negocio = db.relationship("Negocio", backref="resenas")
    usuario = db.relationship("Usuario", backref="resenas")

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
