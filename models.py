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
    descripcion = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(500), nullable=True)

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
