from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- MODELO USUARIO ---
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(100))
    rol = db.Column(db.String(20), default='admin')

# --- MODELO NEGOCIO (CON MAPA) ---
class Negocio(db.Model):
    __tablename__ = 'negocios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    ubicacion = db.Column(db.String(200))

    # --- ESTAS SON LAS COLUMNAS CLAVE ---
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)

    descripcion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    maps_url = db.Column(db.String(500))
    imagen_url = db.Column(db.String(500))

    estado = db.Column(db.String(20), default='pendiente')
    es_vip = db.Column(db.Boolean, default=False)
    calificacion = db.Column(db.Float, default=0.0)
    total_votos = db.Column(db.Integer, default=0)

# --- MODELO NOTICIA ---
class Noticia(db.Model):
    __tablename__ = 'noticias'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    imagen_url = db.Column(db.String(500))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)