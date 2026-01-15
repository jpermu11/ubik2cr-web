import os
import smtplib
import threading
import json
import requests
import time
from email.message import EmailMessage
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # Carga variables del archivo .env

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash
)
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from sqlalchemy import text, or_
from sqlalchemy.pool import QueuePool

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

from models import db, Negocio, Usuario, Noticia, Resena, Oferta, favoritos, Mensaje, ImagenNegocio, Visita

# Importar modelos de vehículos (con manejo seguro de errores)
VEHICULOS_AVAILABLE = False
Vehiculo = None
Agencia = None
ImagenVehiculo = None
favoritos_vehiculos = None

try:
    from models import Vehiculo, Agencia, ImagenVehiculo, favoritos_vehiculos
    VEHICULOS_AVAILABLE = True
    print("[INFO] Modelos de vehículos importados correctamente")
except Exception as e:
    print(f"[WARNING] No se pudieron importar modelos de vehículos: {e}")
    VEHICULOS_AVAILABLE = False
    Vehiculo = None
    Agencia = None
    ImagenVehiculo = None
    favoritos_vehiculos = None


# =====================================================
# APP
# =====================================================
app = Flask(__name__)

# Manejo global de errores para evitar 500
@app.errorhandler(500)
def handle_500_error(e):
    """Manejo de errores 500"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"[ERROR 500] {error_trace}")
    
    # Si es una ruta de admin, mostrar error detallado
    if request.path.startswith('/admin'):
        return f"<h1>Error 500</h1><pre>{error_trace}</pre>", 500
    
    # Para rutas públicas, redirigir a inicio
    flash("Ocurrió un error. Por favor, intentá más tarde.")
    return redirect("/")

@app.errorhandler(Exception)
def handle_exception(e):
    """Manejo de todas las excepciones no capturadas"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"[ERROR] {error_trace}")
    
    # Si es una ruta de admin, mostrar error detallado
    if request.path.startswith('/admin'):
        return f"<h1>Error</h1><pre>{error_trace}</pre>", 500
    
    # Para rutas públicas, redirigir a inicio
    flash("Ocurrió un error. Por favor, intentá más tarde.")
    return redirect("/")

# Agregar filtro personalizado para parsear JSON en templates
@app.template_filter('from_json')
def from_json_filter(value):
    """Filtro para parsear JSON string a lista/dict en templates"""
    if not value:
        return []
    try:
        return json.loads(value)
    except:
        return []


# =====================================================
# SECURITY / SESSION
# =====================================================
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")


# =====================================================
# DATABASE (SOLO DATABASE_URL) + POOL ROBUSTO
# =====================================================
DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()

# Si no hay DATABASE_URL, usar SQLite para desarrollo local
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///app.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # SQLite no necesita pool options
else:
    # Para PostgreSQL: Configurar SSL
    if "sslmode=" not in DATABASE_URL:
        # Usar 'prefer' para desarrollo local, 'require' para producción
        DATABASE_URL += ("&" if "?" in DATABASE_URL else "?") + "sslmode=prefer"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "poolclass": QueuePool,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }


# =====================================================
# CLOUDINARY (para almacenar imágenes permanentemente)
# =====================================================
if CLOUDINARY_AVAILABLE:
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
    api_key = os.environ.get("CLOUDINARY_API_KEY", "").strip()
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
    
    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        USE_CLOUDINARY = True
    else:
        USE_CLOUDINARY = False
else:
    USE_CLOUDINARY = False

# =====================================================
# UPLOADS (fallback local)
# =====================================================
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# =====================================================
# INIT DB + MIGRATIONS
# =====================================================
db.init_app(app)
migrate = Migrate(app, db)


# =====================================================
# HELPERS
# =====================================================
def owner_logged_in() -> bool:
    return "user_id" in session

def admin_logged_in() -> bool:
    return bool(session.get("admin_logged_in"))

def owner_required() -> bool:
    return "user_id" in session

def normalize_password_check(stored: str, plain: str) -> bool:
    if not stored:
        return False
    if stored.startswith(("pbkdf2:", "scrypt:")):
        return check_password_hash(stored, plain)
    return stored == plain

def safe_float(value):
    try:
        v = (value or "").strip()
        return float(v) if v else None
    except Exception:
        return None

def save_upload(field_name: str) -> str:
    """
    Guarda imagen si viene. Devuelve URL.
    Usa Cloudinary si está configurado, sino guarda localmente.
    """
    imagen = request.files.get(field_name)
    if imagen and imagen.filename:
        # Intentar subir a Cloudinary primero
        if USE_CLOUDINARY:
            try:
                result = cloudinary.uploader.upload(
                    imagen,
                    folder="ubik2cr",
                    resource_type="image"
                )
                return result.get("secure_url", "/static/uploads/logo.png")
            except Exception as e:
                print(f"[CLOUDINARY ERROR] {e}")
                # Si falla Cloudinary, intentar guardar localmente
        
        # Fallback: guardar localmente
        try:
            filename = secure_filename(imagen.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            imagen.seek(0)  # Resetear el archivo para leerlo de nuevo
            imagen.save(path)
            return f"/static/uploads/{filename}"
        except Exception:
            # Si falla guardar, usar logo por defecto
            return "/static/uploads/logo.png"
    return "/static/uploads/logo.png"

def save_multiple_uploads(field_name: str, max_files: int = 10) -> list:
    """
    Guarda múltiples imágenes. Devuelve lista de URLs.
    Usa Cloudinary si está configurado, sino guarda localmente.
    """
    urls = []
    files = request.files.getlist(field_name)
    
    # Limitar a max_files
    files = files[:max_files]
    
    for imagen in files:
        if imagen and imagen.filename:
            # Intentar subir a Cloudinary primero
            if USE_CLOUDINARY:
                try:
                    result = cloudinary.uploader.upload(
                        imagen,
                        folder="ubik2cr",
                        resource_type="image"
                    )
                    urls.append(result.get("secure_url"))
                    continue
                except Exception as e:
                    print(f"[CLOUDINARY ERROR] {e}")
            
            # Fallback: guardar localmente
            try:
                filename = secure_filename(imagen.filename)
                path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                imagen.seek(0)
                imagen.save(path)
                urls.append(f"/static/uploads/{filename}")
            except Exception as e:
                print(f"[UPLOAD ERROR] {e}")
                continue
    
    return urls

def get_safe_image_url(imagen_url: str) -> str:
    """
    Devuelve una URL segura para la imagen, con fallback.
    """
    if not imagen_url:
        return "https://via.placeholder.com/600x400?text=Ubik2CR"
    
    # Si es una URL completa, usarla directamente
    if imagen_url.startswith("http://") or imagen_url.startswith("https://"):
        return imagen_url
    
    # Si es una ruta local, verificar si existe
    if imagen_url.startswith("/static/"):
        return imagen_url
    
    # Fallback
    return "https://via.placeholder.com/600x400?text=Ubik2CR"

def parse_horario_from_form(request_form) -> str:
    """
    Parsea el formulario de horarios por día y devuelve JSON string.
    """
    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    horario_dict = {}
    
    for dia in dias:
        abierto = bool(request_form.get(f"horario_{dia}_abierto"))
        if abierto:
            apertura = (request_form.get(f"horario_{dia}_apertura") or "").strip()
            cierre = (request_form.get(f"horario_{dia}_cierre") or "").strip()
            horario_dict[dia] = {
                "abierto": True,
                "apertura": apertura if apertura else None,
                "cierre": cierre if cierre else None
            }
        else:
            horario_dict[dia] = {"abierto": False}
    
    return json.dumps(horario_dict, ensure_ascii=False)

def format_horario_display(horario_json: str, abierto_24h: bool = False) -> str:
    """
    Formatea el horario JSON para mostrar en la vista.
    """
    if abierto_24h:
        return "Abierto 24 horas"
    
    if not horario_json:
        return "Horario no especificado"
    
    try:
        horario_dict = json.loads(horario_json)
    except:
        # Si no es JSON válido, devolver el texto original (compatibilidad)
        return horario_json or "Horario no especificado"
    
    dias_nombres = {
        'lunes': 'Lunes',
        'martes': 'Martes',
        'miercoles': 'Miércoles',
        'jueves': 'Jueves',
        'viernes': 'Viernes',
        'sabado': 'Sábado',
        'domingo': 'Domingo'
    }
    
    partes = []
    for dia, datos in horario_dict.items():
        if datos.get("abierto"):
            apertura = datos.get("apertura", "")
            cierre = datos.get("cierre", "")
            if apertura and cierre:
                partes.append(f"{dias_nombres.get(dia, dia)}: {apertura} - {cierre}")
            elif apertura:
                partes.append(f"{dias_nombres.get(dia, dia)}: {apertura}")
    
    if not partes:
        return "Cerrado"
    
    return "<br>".join(partes)

def get_horario_dict(horario_json: str):
    """
    Obtiene el diccionario de horarios desde JSON.
    """
    if not horario_json:
        return {}
    try:
        return json.loads(horario_json)
    except:
        return {}

def get_productos_tags_list(productos_tags_json: str):
    """
    Obtiene la lista de tags/productos desde JSON.
    """
    if not productos_tags_json:
        return []
    try:
        return json.loads(productos_tags_json)
    except:
        return []


# =====================================================
# EMAIL (para recuperar contraseña)
# =====================================================
def send_email(to_email: str, subject: str, text_body: str, html_body: str = None):
    smtp_host = (os.environ.get("SMTP_HOST") or "").strip()
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = (os.environ.get("SMTP_USER") or "").strip()
    smtp_pass = (os.environ.get("SMTP_PASS") or "").strip()

    # Si tenés SMTP_FROM, lo usamos como display, pero el remitente REAL debe ser smtp_user
    from_display = (os.environ.get("SMTP_FROM") or "Ubik2CR").strip()

    if not (smtp_host and smtp_user and smtp_pass):
        raise RuntimeError("SMTP no configurado (SMTP_HOST/SMTP_USER/SMTP_PASS).")

    msg = EmailMessage()
    # Usar solo el email real como remitente para evitar bloqueos
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    timeout = 20

    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=timeout) as server:
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

def get_base_url_from_request():
    return request.url_root.rstrip("/")


# =====================================================
# PASSWORD RESET TOKENS
# =====================================================
def generate_reset_token(email: str) -> str:
    s = URLSafeTimedSerializer(app.secret_key)
    return s.dumps(email, salt="password-reset")

def verify_reset_token(token: str, expiration: int = 3600):
    s = URLSafeTimedSerializer(app.secret_key)
    try:
        email = s.loads(token, salt="password-reset", max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None


# =====================================================
# MODO MANTENIMIENTO
# =====================================================
# FORZAR MODO MANTENIMIENTO EN RENDER.COM
# En Render.com, el modo mantenimiento está ACTIVADO por defecto
# Para desactivarlo, agrega MAINTENANCE_MODE=false en las variables de entorno de Render.com
# En desarrollo local, está desactivado automáticamente

# Detectar si estamos en Render.com
is_render = os.environ.get("RENDER") is not None or os.environ.get("RENDER_EXTERNAL_HOSTNAME") is not None

# En Render: DESACTIVADO por defecto (para poder trabajar)
# En local: desactivado por defecto (false)
# Se puede sobrescribir con variable de entorno MAINTENANCE_MODE
if is_render:
    # En Render.com: DESACTIVADO por defecto (cambiar a "true" si querés activarlo)
    MAINTENANCE_MODE = os.environ.get("MAINTENANCE_MODE", "false").lower() == "true"
else:
    # En local: DESACTIVADO por defecto
    MAINTENANCE_MODE = os.environ.get("MAINTENANCE_MODE", "false").lower() == "true"

# Este before_request debe ejecutarse PRIMERO (antes de registrar_visita)
@app.before_request
def check_maintenance_mode():
    """Verificar si la aplicación está en modo mantenimiento - SE EJECUTA PRIMERO"""
    if not MAINTENANCE_MODE:
        return None
    
    # Rutas permitidas durante mantenimiento
    path = request.path
    allowed_paths = [
        '/static', '/favicon.ico', '/health', '/health/db',
        '/login', '/logout', '/admin', '/admin/', '/api/',
        '/cuenta', '/owner/login', '/owner/registro', '/panel',
        '/vehiculos', '/vehiculo', '/publicar'
    ]

    # Permitir acceso a rutas de admin y login
    if any(path.startswith(allowed) for allowed in allowed_paths):
        return None

    # Si el usuario es admin o está logueado, permitir acceso
    if admin_logged_in() or owner_logged_in():
        return None
    
    # Para todos los demás, mostrar página de mantenimiento
    from flask import render_template_string
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitio en Mantenimiento | Ubik2CR</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #0b4fa3 0%, #38b24d 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .maintenance-card {
            background: white;
            border-radius: 20px;
            padding: 60px 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 600px;
            margin: 20px;
        }
        .maintenance-icon {
            font-size: 5rem;
            color: #0b4fa3;
            margin-bottom: 30px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        h1 {
            color: #0b4fa3;
            font-weight: bold;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.8;
            margin-bottom: 30px;
        }
        .btn-admin {
            background: linear-gradient(135deg, #0b4fa3, #38b24d);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.3s;
        }
        .btn-admin:hover {
            transform: translateY(-2px);
            color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="maintenance-card">
        <div class="maintenance-icon">
            <i class="fas fa-tools"></i>
        </div>
        <h1>Estamos en Mantenimiento</h1>
        <p>
            Estamos realizando mejoras importantes en nuestro sitio web.
            <br><br>
            <strong>Volveremos pronto con una experiencia mejorada.</strong>
        </p>
        <p style="font-size: 0.9rem; color: #999; margin-top: 40px;">
            Si sos administrador, podés <a href="/login" class="btn-admin">iniciar sesión aquí</a>
        </p>
    </div>
</body>
</html>
    """), 503

# =====================================================
# ANALYTICS - REGISTRAR VISITAS
# =====================================================
@app.before_request
def registrar_visita():
    """Registrar visitas automáticamente (excepto admin y rutas excluidas)"""
    import hashlib
    
    # Rutas excluidas (no registrar)
    path = request.path
    excluded_paths = [
        '/health', '/health/db', '/static', '/favicon.ico',
        '/admin', '/login', '/logout', '/panel', '/owner',
        '/api/', '/_internal'
    ]
    
    # Si es ruta excluida o admin está logueado, no registrar
    if any(path.startswith(excluded) for excluded in excluded_paths):
        return None
    
    # Obtener IP (hashear para privacidad)
    ip = request.remote_addr or 'unknown'
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()
    
    # Obtener datos
    url = request.path
    user_agent = request.headers.get('User-Agent', '')[:200] if request.headers.get('User-Agent') else None
    referrer = request.headers.get('Referer', '')[:500] if request.headers.get('Referer') else None
    
    # Registrar en la base de datos (en background para no bloquear)
    try:
        visita = Visita(
            ip_hash=ip_hash,
            url=url,
            user_agent=user_agent,
            referrer=referrer,
            created_at=datetime.utcnow()
        )
        db.session.add(visita)
        db.session.commit()
    except Exception as e:
        # Si falla, no afectar la experiencia del usuario
        db.session.rollback()
        pass
    
    return None


# =====================================================
# HEALTH CHECK
# =====================================================
@app.route("/health")
def health():
    return {"status": "ok"}, 200

@app.route("/health/db")
def health_db():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "db_error", "error": str(e)}, 500


# =====================================================
# PUBLIC ROUTES
# =====================================================
@app.route("/")
def inicio():
    """Página principal - Búsqueda de vehículos"""
    # Si los modelos no están disponibles, mostrar página de vehículos vacía
    if not VEHICULOS_AVAILABLE:
        # Mostrar página de vehículos aunque no haya datos
        import os
        json_path = os.path.join(os.path.dirname(__file__), "static", "data", "costa_rica_ubicaciones.json")
        ubicaciones_data = {}
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                ubicaciones_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] No se pudo cargar ubicaciones: {e}")
        
        return render_template(
            "vehiculos_index.html",
            vehiculos=[],
            total=0,
            page=1,
            total_pages=1,
            has_prev=False,
            has_next=False,
            prev_page=1,
            next_page=1,
            q="",
            marcas=[],
            ubicaciones_data=ubicaciones_data,
            marca_actual="",
            modelo_actual="",
            año_desde_actual="",
            año_hasta_actual="",
            precio_min_actual="",
            precio_max_actual="",
            km_min_actual="",
            km_max_actual="",
            tipo_actual="",
            transmision_actual="",
            combustible_actual="",
            provincia_actual="",
            canton_actual="",
            estado_vehiculo_actual="",
            ordenar_actual="recientes"
        )
    
    # BÚSQUEDA DE VEHÍCULOS
    busqueda_original = (request.args.get("q") or "").strip()
    q = busqueda_original.lower()
    
    # Filtros
    marca_filtro = request.args.get("marca", "").strip()
    modelo_filtro = request.args.get("modelo", "").strip()
    año_desde = request.args.get("año_desde", "").strip()
    año_hasta = request.args.get("año_hasta", "").strip()
    precio_min = request.args.get("precio_min", "").strip()
    precio_max = request.args.get("precio_max", "").strip()
    km_min = request.args.get("km_min", "").strip()
    km_max = request.args.get("km_max", "").strip()
    tipo_filtro = request.args.get("tipo", "").strip()
    transmision_filtro = request.args.get("transmision", "").strip()
    combustible_filtro = request.args.get("combustible", "").strip()
    provincia_filtro = request.args.get("provincia", "").strip()
    canton_filtro = request.args.get("canton", "").strip()
    estado_vehiculo_filtro = request.args.get("estado_vehiculo", "").strip()
    ordenar = request.args.get("ordenar", "recientes").strip()
    
    # Paginación
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    if page < 1:
        page = 1
    
    PER_PAGE = 24
    
    # Query base: solo vehículos aprobados (con manejo de errores)
    try:
        query = Vehiculo.query.filter_by(estado="aprobado")
    except Exception as e:
        print(f"[ERROR] No se puede consultar vehículos: {e}")
        # Retornar página vacía
        import os
        json_path = os.path.join(os.path.dirname(__file__), "static", "data", "costa_rica_ubicaciones.json")
        ubicaciones_data = {}
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                ubicaciones_data = json.load(f)
        except:
            pass
        
        return render_template(
            "vehiculos_index.html",
            vehiculos=[],
            total=0,
            page=1,
            total_pages=1,
            has_prev=False,
            has_next=False,
            prev_page=1,
            next_page=1,
            q="",
            marcas=[],
            ubicaciones_data=ubicaciones_data,
            marca_actual="",
            modelo_actual="",
            año_desde_actual="",
            año_hasta_actual="",
            precio_min_actual="",
            precio_max_actual="",
            km_min_actual="",
            km_max_actual="",
            tipo_actual="",
            transmision_actual="",
            combustible_actual="",
            provincia_actual="",
            canton_actual="",
            estado_vehiculo_actual="",
            ordenar_actual="recientes"
        )
    
    # Aplicar filtros
    if marca_filtro:
        query = query.filter_by(marca=marca_filtro)
    if modelo_filtro:
        query = query.filter_by(modelo=modelo_filtro)
    if año_desde:
        try:
            query = query.filter(Vehiculo.año >= int(año_desde))
        except ValueError:
            pass
    if año_hasta:
        try:
            query = query.filter(Vehiculo.año <= int(año_hasta))
        except ValueError:
            pass
    if precio_min:
        try:
            query = query.filter(Vehiculo.precio >= float(precio_min))
        except ValueError:
            pass
    if precio_max:
        try:
            query = query.filter(Vehiculo.precio <= float(precio_max))
        except ValueError:
            pass
    if km_min:
        try:
            query = query.filter(Vehiculo.kilometraje >= int(km_min))
        except ValueError:
            pass
    if km_max:
        try:
            query = query.filter(Vehiculo.kilometraje <= int(km_max))
        except ValueError:
            pass
    if tipo_filtro:
        query = query.filter_by(tipo_vehiculo=tipo_filtro)
    if transmision_filtro:
        query = query.filter_by(transmision=transmision_filtro)
    if combustible_filtro:
        query = query.filter_by(combustible=combustible_filtro)
    if provincia_filtro:
        query = query.filter_by(provincia=provincia_filtro)
    if canton_filtro:
        query = query.filter_by(canton=canton_filtro)
    if estado_vehiculo_filtro:
        query = query.filter_by(estado_vehiculo=estado_vehiculo_filtro)
    
    # Búsqueda por texto
    if q:
        query = query.filter(
            or_(
                Vehiculo.marca.ilike(f"%{q}%"),
                Vehiculo.modelo.ilike(f"%{q}%"),
                Vehiculo.descripcion.ilike(f"%{q}%")
            )
        )
    
    # Ordenamiento
    if ordenar == "recientes":
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.created_at.desc())
    elif ordenar == "antiguos":
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.created_at.asc())
    elif ordenar == "precio_asc":
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.precio.asc())
    elif ordenar == "precio_desc":
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.precio.desc())
    elif ordenar == "km_asc":
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.kilometraje.asc())
    elif ordenar == "km_desc":
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.kilometraje.desc())
    elif ordenar == "destacados":
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.created_at.desc())
    else:
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.created_at.desc())
    
    total = query.count()
    total_pages = (total + PER_PAGE - 1) // PER_PAGE if total > 0 else 1
    if page > total_pages:
        page = total_pages
    
    vehiculos = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()
    
    # Obtener marcas únicas para el dropdown
    try:
        marcas_unicas = db.session.query(Vehiculo.marca).filter_by(estado="aprobado").distinct().order_by(Vehiculo.marca).all()
        marcas = [m[0] for m in marcas_unicas]
    except Exception as e:
        print(f"[ERROR] No se pueden obtener marcas: {e}")
        marcas = []
    
    # Cargar datos de ubicaciones
    import os
    json_path = os.path.join(os.path.dirname(__file__), "static", "data", "costa_rica_ubicaciones.json")
    ubicaciones_data = {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            ubicaciones_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar ubicaciones: {e}")
    
    return render_template(
        "vehiculos_index.html",
        vehiculos=vehiculos,
        total=total,
        page=page,
        total_pages=total_pages,
        has_prev=page > 1,
        has_next=page < total_pages,
        prev_page=page - 1,
        next_page=page + 1,
        q=busqueda_original,
        marcas=marcas,
        ubicaciones_data=ubicaciones_data,
        # Pasar filtros actuales
        marca_actual=marca_filtro,
        modelo_actual=modelo_filtro,
        año_desde_actual=año_desde,
        año_hasta_actual=año_hasta,
        precio_min_actual=precio_min,
        precio_max_actual=precio_max,
        km_min_actual=km_min,
        km_max_actual=km_max,
        tipo_actual=tipo_filtro,
        transmision_actual=transmision_filtro,
        combustible_actual=combustible_filtro,
        provincia_actual=provincia_filtro,
        canton_actual=canton_filtro,
        estado_vehiculo_actual=estado_vehiculo_filtro,
        ordenar_actual=ordenar
    )

def inicio_negocios():
    # Obtener ofertas activas (no expiradas y de negocios aprobados)
    ahora = datetime.utcnow()
    ofertas_activas = Oferta.query.join(Negocio).filter(
        Negocio.estado == "aprobado",
        Oferta.fecha_caducidad >= ahora,
        Oferta.estado == "activa"
    ).order_by(Oferta.fecha_inicio.desc()).limit(10).all()
    
    # Obtener noticias recientes (no caducadas)
    noticias_recientes = Noticia.query.filter(
        or_(
            Noticia.fecha_caducidad.is_(None),
            Noticia.fecha_caducidad >= ahora
        )
    ).order_by(Noticia.fecha.desc()).limit(5).all()
    
    busqueda_original = (request.args.get("q") or "").strip()  # Original con mayúsculas
    q = busqueda_original.lower()  # Lowercase para búsqueda
    cat = (request.args.get("cat") or "Todas").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    if page < 1:
        page = 1

    PER_PAGE = 24

    # Query base: solo negocios aprobados (todos, sin importar si tienen ubicación completa)
    query = Negocio.query.filter_by(estado="aprobado")

    # =====================================================
    # BÚSQUEDA INTELIGENTE CON IA - MAPEO DE PALABRAS CLAVE
    # =====================================================
    def buscar_categorias_inteligente(busqueda):
        """Mapea productos/servicios comunes a categorías de negocios"""
        busqueda_lower = busqueda.lower().strip()
        categorias_sugeridas = []
        
        # Diccionario de mapeo: producto/servicio -> categorías relacionadas
        mapeo_inteligente = {
            # Productos de belleza y cuidado personal
            "shampoo": ["Farmacias", "Supermercados", "Tiendas de Belleza", "Salones de Belleza"],
            "shampú": ["Farmacias", "Supermercados", "Tiendas de Belleza", "Salones de Belleza"],
            "champú": ["Farmacias", "Supermercados", "Tiendas de Belleza", "Salones de Belleza"],
            "jabon": ["Farmacias", "Supermercados", "Tiendas de Belleza"],
            "jabón": ["Farmacias", "Supermercados", "Tiendas de Belleza"],
            "crema": ["Farmacias", "Supermercados", "Tiendas de Belleza"],
            "maquillaje": ["Tiendas de Belleza", "Farmacias", "Salones de Belleza"],
            "perfume": ["Farmacias", "Tiendas de Belleza", "Supermercados"],
            "corte": ["Salones de Belleza", "Barberías"],
            "pelo": ["Salones de Belleza", "Barberías", "Tiendas de Belleza"],
            "cabello": ["Salones de Belleza", "Barberías", "Tiendas de Belleza"],
            "uñas": ["Salones de Belleza", "Manicure y Pedicure"],
            
            # Medicinas y salud
            "medicina": ["Farmacias", "Clínicas", "Hospitales"],
            "medicamento": ["Farmacias"],
            "pastilla": ["Farmacias"],
            "vitamina": ["Farmacias", "Suplementos"],
            "doctor": ["Clínicas", "Consultorios Médicos", "Hospitales"],
            "médico": ["Clínicas", "Consultorios Médicos", "Hospitales"],
            "hospital": ["Hospitales", "Clínicas"],
            "clinica": ["Clínicas", "Consultorios Médicos"],
            "dentista": ["Odontología", "Clínicas"],
            "fisioterapia": ["Fisioterapia", "Clínicas"],
            
            # Comida y bebidas
            "comida": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Supermercados"],
            "restaurante": ["Sodas y Rest.", "Restaurante", "Comida Rápida"],
            "pizza": ["Comida Rápida", "Pizzerías", "Restaurante"],
            "hamburguesa": ["Comida Rápida", "Restaurante"],
            "cafe": ["Cafeterías", "Restaurante"],
            "café": ["Cafeterías", "Restaurante"],
            "desayuno": ["Sodas y Rest.", "Restaurante", "Cafeterías"],
            "almuerzo": ["Sodas y Rest.", "Restaurante", "Comida Rápida"],
            "cena": ["Restaurante", "Sodas y Rest.", "Bares y Licores"],
            "bebida": ["Bares y Licores", "Supermercados", "Restaurante"],
            "cerveza": ["Bares y Licores", "Supermercados"],
            "helado": ["Heladerías", "Supermercados"],
            "postre": ["Heladerías", "Restaurante", "Panaderías"],
            
            # Supermercados y alimentos
            "supermercado": ["Supermercados", "Verdulerías", "Carnicerías"],
            "verduras": ["Verdulerías", "Supermercados"],
            "frutas": ["Verdulerías", "Supermercados"],
            "carne": ["Carnicerías", "Supermercados"],
            "pan": ["Panaderías", "Supermercados"],
            "leche": ["Supermercados", "Farmacias"],
            "huevos": ["Supermercados", "Verdulerías"],
            
            # Servicios
            "gasolina": ["Gasolineras", "Estaciones de Servicio"],
            "combustible": ["Gasolineras", "Estaciones de Servicio"],
            "taller": ["Talleres Mecánicos", "Talleres de Reparación"],
            "mecanico": ["Talleres Mecánicos", "Talleres de Reparación"],
            "mecánico": ["Talleres Mecánicos", "Talleres de Reparación"],
            "lavado": ["Lavado de Autos", "Lavanderías"],
            "lavanderia": ["Lavanderías"],
            "hotel": ["Hoteles", "Alojamiento"],
            "motel": ["Hoteles", "Alojamiento"],
            
            # Educación
            "escuela": ["Escuelas", "Centros Educativos"],
            "colegio": ["Escuelas", "Centros Educativos"],
            "universidad": ["Universidades", "Centros Educativos"],
            "curso": ["Centros Educativos", "Academias"],
            
            # Tecnología
            "computadora": ["Tiendas de Tecnología", "Reparación de Equipos"],
            "celular": ["Tiendas de Tecnología", "Reparación de Equipos"],
            "telefono": ["Tiendas de Tecnología", "Reparación de Equipos"],
            "internet": ["Servicios de Internet", "Cafés Internet"],
            
            # Servicios financieros
            "banco": ["Bancos", "Cooperativas"],
            "cajero": ["Bancos", "Cooperativas"],
            "dinero": ["Bancos", "Cooperativas"],
            
            # Herramientas y ferretería (ejemplo del usuario: martillo)
            "martillo": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "clavo": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "clavos": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "herramienta": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "herramientas": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "pintura": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "tornillo": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "tornillos": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "destornillador": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "taladro": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "ferreteria": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            "ferretería": ["Ferreterías", "Agrocomerciales", "Ferreterías y Materiales"],
            
            # Comida rápida (ejemplo del usuario: hamburguesa)
            "hamburguesa": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Pizzerías"],
            "hamburguesas": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Pizzerías"],
            "papas fritas": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Pizzerías"],
            "papas": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Verdurerías", "Supermercados"],
            "refresco": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Supermercados", "Bares y Licores"],
            "refrescos": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Supermercados", "Bares y Licores"],
            "gaseosa": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Supermercados", "Bares y Licores"],
            "gaseosas": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Supermercados", "Bares y Licores"],
            "sandwich": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Cafeterías"],
            "sandwiches": ["Sodas y Rest.", "Restaurante", "Comida Rápida", "Cafeterías"],
            "soda": ["Sodas y Rest.", "Restaurante", "Comida Rápida"],
            "casado": ["Sodas y Rest.", "Restaurante"],
            "arroz con pollo": ["Sodas y Rest.", "Restaurante"],
            "gallo pinto": ["Sodas y Rest.", "Restaurante", "Cafeterías"],
        }
        
        # Buscar coincidencias
        palabras_busqueda = busqueda_lower.split()
        for palabra in palabras_busqueda:
            if palabra in mapeo_inteligente:
                categorias_sugeridas.extend(mapeo_inteligente[palabra])
        
        # También buscar coincidencias parciales
        for clave, categorias in mapeo_inteligente.items():
            if clave in busqueda_lower or busqueda_lower in clave:
                categorias_sugeridas.extend(categorias)
        
        # Eliminar duplicados y devolver
        return list(set(categorias_sugeridas))
    
    # Filtros de ubicación (OPCIONALES - solo se aplican si el usuario los selecciona para refinar la búsqueda)
    provincia_filtro = request.args.get("provincia", "").strip()
    canton_filtro = request.args.get("canton", "").strip()
    distrito_filtro = request.args.get("distrito", "").strip()
    
    # Solo aplicar filtros de ubicación si el usuario los seleccionó explícitamente
    if provincia_filtro:
        query = query.filter_by(provincia=provincia_filtro)
    if canton_filtro:
        query = query.filter_by(canton=canton_filtro)
    if distrito_filtro:
        query = query.filter_by(distrito=distrito_filtro)
    
    # Aplicar búsqueda inteligente (solo si hay texto de búsqueda)
    categorias_inteligentes = []
    if q:
        categorias_inteligentes = buscar_categorias_inteligente(q)
        
        # Construir filtro: buscar en nombre, descripción, ubicación, tags Y categorías inteligentes
        condiciones_busqueda = [
            Negocio.nombre.ilike(f"%{q}%"),
            Negocio.descripcion.ilike(f"%{q}%"),
            Negocio.ubicacion.ilike(f"%{q}%")
        ]
        
        # BUSCAR EN PRODUCTOS_TAGS (tags personalizados del negocio) - BÚSQUEDA INTELIGENTE
        # Los tags están almacenados como JSON string: ["martillo", "clavos", "pintura"]
        # Buscar si el término de búsqueda está en los tags
        try:
            # Buscar en tags JSON usando LIKE (funciona con postgresql y sqlite)
            # Búsqueda más inteligente: busca el término completo dentro del JSON
            palabras_busqueda = q.split()
            
            condiciones_tags = []
            for palabra in palabras_busqueda:
                if palabra and len(palabra) > 2:  # Solo buscar palabras de más de 2 caracteres
                    condiciones_tags.extend([
                        Negocio.productos_tags.ilike(f'%"{palabra}"%'),      # Búsqueda exacta: "martillo"
                        Negocio.productos_tags.ilike(f'%"{palabra} %'),      # Búsqueda al inicio
                        Negocio.productos_tags.ilike(f'% "{palabra}"%'),     # Búsqueda con espacio antes
                        Negocio.productos_tags.ilike(f'%{palabra}%')         # Búsqueda parcial
                    ])
            
            # También buscar el término completo
            if q and len(q) > 2:
                condiciones_tags.extend([
                    Negocio.productos_tags.ilike(f'%"{q}"%'),
                    Negocio.productos_tags.ilike(f'%{q}%')
                ])
            
            if condiciones_tags:
                condiciones_busqueda.append(or_(*condiciones_tags))
        except Exception as e:
            print(f"[BUSQUEDA] Error al buscar en tags: {e}")
            # Si hay error, continuar sin buscar en tags
        
        # Si encontramos categorías inteligentes, agregarlas al filtro
        if categorias_inteligentes:
            condiciones_busqueda.append(Negocio.categoria.in_(categorias_inteligentes))
        
        query = query.filter(or_(*condiciones_busqueda))
    
    # Filtro de categoría (aplicar después de ubicación pero antes del ordenamiento)
    if cat and cat != "Todas":
        query = query.filter_by(categoria=cat)

    query = query.order_by(Negocio.es_vip.desc(), Negocio.id.desc())

    total = query.count()
    total_pages = (total + PER_PAGE - 1) // PER_PAGE if total > 0 else 1
    if page > total_pages:
        page = total_pages

    negocios = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()

    return render_template(
        "index.html",
        negocios=negocios,
        categoria_actual=cat,
        page=page,
        total_pages=total_pages,
        has_prev=page > 1,
        has_next=page < total_pages,
        prev_page=page - 1,
        next_page=page + 1,
        q=busqueda_original if q else "",
        cat=cat,
        ofertas_activas=ofertas_activas,
        noticias_recientes=noticias_recientes,
        owner_logged_in=owner_logged_in(),
        admin_logged_in=admin_logged_in(),
        get_safe_image_url=get_safe_image_url,
        categorias_inteligentes=categorias_inteligentes if q else [],
    )

@app.route("/api/ubicaciones/cantones")
def api_cantones():
    """API para obtener cantones de una provincia"""
    provincia = request.args.get("provincia", "").strip()
    if not provincia:
        return {"error": "Provincia requerida"}, 400
    
    try:
        import os
        json_path = os.path.join(os.path.dirname(__file__), "static", "data", "costa_rica_ubicaciones.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if provincia in data:
            cantones = list(data[provincia].keys())
            return {"cantones": cantones}
        else:
            return {"cantones": []}
    except Exception as e:
        print(f"[API ERROR] Error al obtener cantones: {e}")
        return {"error": "Error al cargar datos"}, 500

@app.route("/api/vehiculos/modelos")
def api_modelos_vehiculos():
    """API para obtener modelos de una marca"""
    marca = request.args.get("marca", "").strip()
    if not marca:
        return {"error": "Marca requerida"}, 400
    
    if not VEHICULOS_AVAILABLE:
        return {"modelos": []}
    
    try:
        modelos_unicos = db.session.query(Vehiculo.modelo).filter_by(
            marca=marca,
            estado="aprobado"
        ).distinct().order_by(Vehiculo.modelo).all()
        modelos = [m[0] for m in modelos_unicos]
        return {"modelos": modelos}
    except Exception as e:
        print(f"[API ERROR] Error al obtener modelos: {e}")
        return {"modelos": []}

@app.route("/api/ubicaciones/distritos")
def api_distritos():
    """API para obtener distritos de un cantón"""
    provincia = request.args.get("provincia", "").strip()
    canton = request.args.get("canton", "").strip()
    
    if not provincia or not canton:
        return {"error": "Provincia y cantón requeridos"}, 400
    
    try:
        import os
        json_path = os.path.join(os.path.dirname(__file__), "static", "data", "costa_rica_ubicaciones.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if provincia in data and canton in data[provincia]:
            distritos = data[provincia][canton]
            return {"distritos": distritos}
        else:
            return {"distritos": []}
    except Exception as e:
        print(f"[API ERROR] Error al obtener distritos: {e}")
        return {"error": "Error al cargar datos"}, 500

@app.route("/cuenta")
def cuenta():
    return render_template("cuenta.html")

@app.route("/ayuda")
def ayuda():
    """Página de ayuda y manual de usuario"""
    return render_template("ayuda.html")

@app.route("/favoritos")
def ver_favoritos():
    """Muestra los negocios favoritos del usuario"""
    if not owner_logged_in():
        flash("Iniciá sesión para ver tus favoritos.")
        return redirect("/cuenta")
    
    # Obtener IDs de negocios favoritos del usuario
    user_id = session.get("user_id")
    favoritos_query = db.session.execute(
        text("SELECT negocio_id FROM favoritos WHERE usuario_id = :user_id"),
        {"user_id": user_id}
    ).fetchall()
    favoritos_ids = [f[0] for f in favoritos_query]
    
    if not favoritos_ids:
        negocios = []
    else:
        negocios = Negocio.query.filter(
            Negocio.id.in_(favoritos_ids),
            Negocio.estado == "aprobado"
        ).order_by(Negocio.es_vip.desc(), Negocio.id.desc()).all()
    
    return render_template(
        "favoritos.html",
        negocios=negocios,
        total=len(negocios),
        get_safe_image_url=get_safe_image_url
    )

@app.route("/favoritos/agregar/<int:negocio_id>")
def agregar_favorito(negocio_id):
    """Agrega un negocio a favoritos"""
    if not owner_logged_in():
        return {"error": "Debes iniciar sesión"}, 401
    
    user_id = session.get("user_id")
    negocio = db.session.get(Negocio, negocio_id)
    
    if not negocio:
        return {"error": "Negocio no encontrado"}, 404
    
    # Verificar si ya está en favoritos
    existe = db.session.execute(
        text("SELECT 1 FROM favoritos WHERE usuario_id = :user_id AND negocio_id = :negocio_id"),
        {"user_id": user_id, "negocio_id": negocio_id}
    ).fetchone()
    
    if existe:
        return {"message": "Ya está en favoritos", "es_favorito": True}, 200
    
    # Agregar a favoritos
    db.session.execute(
        text("INSERT INTO favoritos (usuario_id, negocio_id, created_at) VALUES (:user_id, :negocio_id, :created_at)"),
        {"user_id": user_id, "negocio_id": negocio_id, "created_at": datetime.utcnow()}
    )
    db.session.commit()
    
    return {"message": "Agregado a favoritos", "es_favorito": True}, 200

@app.route("/favoritos/quitar/<int:negocio_id>")
def quitar_favorito(negocio_id):
    """Quita un negocio de favoritos"""
    if not owner_logged_in():
        return {"error": "Debes iniciar sesión"}, 401
    
    user_id = session.get("user_id")
    
    # Quitar de favoritos
    db.session.execute(
        text("DELETE FROM favoritos WHERE usuario_id = :user_id AND negocio_id = :negocio_id"),
        {"user_id": user_id, "negocio_id": negocio_id}
    )
    db.session.commit()
    
    return {"message": "Eliminado de favoritos", "es_favorito": False}, 200

@app.route("/api/favoritos/<int:negocio_id>")
def es_favorito(negocio_id):
    """Verifica si un negocio está en favoritos"""
    if not owner_logged_in():
        return {"es_favorito": False}, 200
    
    user_id = session.get("user_id")
    existe = db.session.execute(
        text("SELECT 1 FROM favoritos WHERE usuario_id = :user_id AND negocio_id = :negocio_id"),
        {"user_id": user_id, "negocio_id": negocio_id}
    ).fetchone()
    
    return {"es_favorito": bool(existe)}, 200

@app.route("/mapa")
def ver_mapa():
    negocios = (
        Negocio.query.filter_by(estado="aprobado")
        .order_by(Negocio.es_vip.desc(), Negocio.id.desc())
        .all()
    )
    return render_template("mapa.html", negocios=negocios)

@app.route("/noticias")
def noticias():
    # Filtrar noticias que no han caducado (fecha_caducidad es None o es futura)
    ahora = datetime.utcnow()
    noticias_list = Noticia.query.filter(
        or_(
            Noticia.fecha_caducidad.is_(None),
            Noticia.fecha_caducidad >= ahora
        )
    ).order_by(Noticia.fecha.desc()).all()
    return render_template("noticias.html", noticias=noticias_list, get_safe_image_url=get_safe_image_url)

@app.route("/noticia/<int:id>")
def detalle_noticia(id):
    """Ver detalle de una noticia"""
    noticia = db.session.get(Noticia, id)
    if not noticia:
        return "Noticia no encontrada", 404
    
    # Verificar si está caducada
    ahora = datetime.utcnow()
    esta_caducada = False
    if noticia.fecha_caducidad and noticia.fecha_caducidad <= ahora:
        esta_caducada = True
    
    return render_template(
        "detalle_noticia.html",
        noticia=noticia,
        esta_caducada=esta_caducada,
        get_safe_image_url=get_safe_image_url
    )

@app.route("/oferta/<int:id>")
def detalle_oferta(id):
    """Ver detalle de una oferta"""
    oferta = db.session.get(Oferta, id)
    if not oferta:
        return "Oferta no encontrada", 404
    
    # Verificar si está expirada
    ahora = datetime.utcnow()
    esta_expirada = oferta.fecha_caducidad <= ahora or oferta.estado != "activa"
    
    # Obtener el negocio asociado
    negocio = db.session.get(Negocio, oferta.negocio_id)
    
    return render_template(
        "detalle_oferta.html",
        oferta=oferta,
        negocio=negocio,
        esta_expirada=esta_expirada,
        get_safe_image_url=get_safe_image_url
    )

@app.route("/negocio/<int:id>")
def detalle_negocio(id):
    n = db.session.get(Negocio, id)
    if not n:
        return "Negocio no encontrado", 404
    
    # Obtener reseñas aprobadas
    resenas = Resena.query.filter_by(
        negocio_id=id,
        estado="aprobado"
    ).order_by(Resena.created_at.desc()).limit(50).all()
    
    # Calcular estadísticas
    total_resenas = len(resenas)
    promedio = n.calificacion if n.calificacion else 0.0
    
    return render_template(
        "detalle.html",
        n=n,
        resenas=resenas,
        total_resenas=total_resenas,
        promedio=promedio,
        get_safe_image_url=get_safe_image_url,
        format_horario_display=format_horario_display,
        get_horario_dict=get_horario_dict
    )

@app.route("/negocio/<int:negocio_id>/resena", methods=["POST"])
def crear_resena(negocio_id):
    """Crear una nueva reseña"""
    negocio = db.session.get(Negocio, negocio_id)
    if not negocio:
        return redirect("/")
    
    if negocio.estado != "aprobado":
        flash("Este negocio aún no está aprobado.")
        return redirect(f"/negocio/{negocio_id}")
    
    calificacion = int(request.form.get("calificacion", 0))
    comentario = (request.form.get("comentario") or "").strip()
    nombre = (request.form.get("nombre") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    
    # Validaciones
    if calificacion < 1 or calificacion > 5:
        flash("La calificación debe ser entre 1 y 5 estrellas.")
        return redirect(f"/negocio/{negocio_id}")
    
    if not comentario or len(comentario) < 10:
        flash("El comentario debe tener al menos 10 caracteres.")
        return redirect(f"/negocio/{negocio_id}")
    
    # Obtener usuario si está logueado
    usuario_id = session.get("user_id") if owner_logged_in() else None
    
    # Si no está logueado, requiere nombre y email
    if not usuario_id:
        if not nombre or not email:
            flash("Para dejar una reseña anónima, necesitás nombre y email.")
            return redirect(f"/negocio/{negocio_id}")
    
    # Crear reseña
    nueva_resena = Resena(
        negocio_id=negocio_id,
        usuario_id=usuario_id,
        nombre_usuario=nombre if not usuario_id else None,
        email_usuario=email if not usuario_id else None,
        calificacion=calificacion,
        comentario=comentario,
        estado="aprobado"  # Por ahora aprobamos automáticamente, luego se puede moderar
    )
    
    db.session.add(nueva_resena)
    
    # Actualizar calificación promedio del negocio
    todas_resenas = Resena.query.filter_by(
        negocio_id=negocio_id,
        estado="aprobado"
    ).all()
    
    if todas_resenas:
        promedio = sum(r.calificacion for r in todas_resenas) / len(todas_resenas)
        negocio.calificacion = round(promedio, 1)
        negocio.total_votos = len(todas_resenas)
    
    db.session.commit()
    
    flash("¡Gracias por tu reseña!")
    return redirect(f"/negocio/{negocio_id}")


# =====================================================
# MENSAJERÍA PRIVADA
# =====================================================
@app.route("/negocio/<int:negocio_id>/mensaje", methods=["POST"])
def enviar_mensaje(negocio_id):
    """Enviar mensaje a un negocio"""
    negocio = db.session.get(Negocio, negocio_id)
    if not negocio or negocio.estado != "aprobado":
        flash("Negocio no encontrado o no disponible.")
        return redirect("/")
    
    nombre = (request.form.get("nombre") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    asunto = (request.form.get("asunto") or "").strip()
    mensaje_texto = (request.form.get("mensaje") or "").strip()
    
    # Validaciones
    if not nombre or len(nombre) < 2:
        flash("El nombre debe tener al menos 2 caracteres.")
        return redirect(f"/negocio/{negocio_id}")
    
    if not email or "@" not in email:
        flash("Debés proporcionar un email válido.")
        return redirect(f"/negocio/{negocio_id}")
    
    if not asunto or len(asunto) < 3:
        flash("El asunto debe tener al menos 3 caracteres.")
        return redirect(f"/negocio/{negocio_id}")
    
    if not mensaje_texto or len(mensaje_texto) < 10:
        flash("El mensaje debe tener al menos 10 caracteres.")
        return redirect(f"/negocio/{negocio_id}")
    
    # Obtener usuario si está logueado
    usuario_id = session.get("user_id") if owner_logged_in() else None
    
    # Crear mensaje
    nuevo_mensaje = Mensaje(
        negocio_id=negocio_id,
        usuario_id=usuario_id,
        nombre_remitente=nombre,
        email_remitente=email,
        asunto=asunto,
        mensaje=mensaje_texto,
        leido=False,
        respondido=False
    )
    
    db.session.add(nuevo_mensaje)
    db.session.commit()
    
    # Enviar notificación por email al dueño del negocio
    owner = db.session.get(Usuario, negocio.owner_id) if negocio.owner_id else None
    if owner and owner.email:
        try:
            base_url = get_base_url_from_request()
            mensajes_url = f"{base_url}/panel/mensajes"
            negocio_url = f"{base_url}/negocio/{negocio.id}"
            
            # Mensaje adaptado para vehículos (cuando se implemente)
            text_body = (
                f"Hola {owner.nombre or 'vendedor'},\n\n"
                f"Has recibido un nuevo contacto sobre tu publicación.\n\n"
                f"Remitente: {nombre} ({email})\n"
                f"Asunto: {asunto}\n\n"
                f"Mensaje:\n{mensaje_texto}\n\n"
            )
            
            # Si el método es WhatsApp, agregar link
            if metodo_contacto == "whatsapp" and negocio.whatsapp:
                whatsapp_link = f"https://wa.me/{negocio.whatsapp.replace('+', '').replace('-', '').replace(' ', '')}?text=Hola, te contacto desde Ubik2CR sobre: {asunto}"
                text_body += f"Contactar por WhatsApp: {whatsapp_link}\n\n"
            
            text_body += f"Podés responder directamente a: {email}\n\n"
            text_body += "El equipo de Ubik2CR"
            
            html_body = f"""
            <div style="font-family:Arial,sans-serif;background:#f5f7fa;padding:24px">
                <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e6e8ee">
                    <div style="background:linear-gradient(90deg,#0b4fa3,#38b24d);color:#fff;padding:18px 20px">
                        <div style="font-size:18px;font-weight:800">Ubik2CR</div>
                        <div style="opacity:.9;font-size:13px;margin-top:4px">Nuevo Mensaje</div>
                    </div>
                    <div style="padding:18px 20px;color:#111827">
                        <p style="margin:0 0 10px 0">Hola {owner.nombre or 'dueño del negocio'},</p>
                        <p style="margin:0 0 14px 0;line-height:1.5">
                            Has recibido un nuevo mensaje para tu negocio <b>{negocio.nombre}</b>.
                        </p>
                        <div style="background:#f9fafb;padding:15px;border-radius:10px;margin:15px 0">
                            <div style="margin-bottom:10px">
                                <strong style="color:#6b7280;font-size:12px">Remitente:</strong>
                                <div style="color:#111827;font-weight:600">{nombre}</div>
                                <div style="color:#6b7280;font-size:13px">{email}</div>
                            </div>
                            <div style="margin-bottom:10px">
                                <strong style="color:#6b7280;font-size:12px">Asunto:</strong>
                                <div style="color:#111827">{asunto}</div>
                            </div>
                            <div>
                                <strong style="color:#6b7280;font-size:12px">Mensaje:</strong>
                                <div style="color:#111827;margin-top:5px;white-space:pre-wrap;line-height:1.5">{mensaje_texto}</div>
                            </div>
                        </div>
                        <div style="text-align:center;margin:18px 0">
                            <a href="{mensajes_url}" style="display:inline-block;background:#0b4fa3;color:#fff;text-decoration:none;padding:12px 16px;border-radius:10px;font-weight:700">
                                Ver y Responder Mensaje
                            </a>
                        </div>
                        <p style="margin:15px 0 0 0;font-size:13px;color:#6b7280;line-height:1.5">
                            <a href="{negocio_url}" style="color:#0b4fa3;text-decoration:none">Ver tu negocio</a>
                        </p>
                    </div>
                </div>
                <div style="max-width:520px;margin:10px auto 0 auto;font-size:12px;color:#6b7280;text-align:center">
                    © {datetime.now().year} Ubik2CR
                </div>
            </div>
            """
            
            send_email(owner.email, f"Nuevo contacto desde Ubik2CR: {asunto}", text_body, html_body)
        except Exception as e:
            print(f"[EMAIL ERROR] No se pudo enviar notificación a {owner.email}: {e}")
    
    # Si es WhatsApp, también enviar link directo
    if metodo_contacto == "whatsapp" and negocio.whatsapp:
        flash(f"¡Contacto enviado! Podés contactar directamente por WhatsApp.")
    else:
        flash("¡Mensaje enviado exitosamente! El vendedor recibirá una notificación por email.")
    
    return redirect(f"/negocio/{negocio_id}")


@app.route("/panel/mensajes")
def ver_mensajes():
    """Ver mensajes recibidos para los negocios del dueño"""
    if not owner_required():
        return redirect("/cuenta")
    
    user_id = session["user_id"]
    
    # Obtener todos los negocios del dueño
    negocios = Negocio.query.filter_by(owner_id=user_id).all()
    negocios_ids = [n.id for n in negocios]
    
    if not negocios_ids:
        return render_template("mensajes.html", mensajes=[], negocios={}, sin_negocios=True)
    
    # Obtener mensajes de los negocios del dueño
    mensajes = Mensaje.query.filter(
        Mensaje.negocio_id.in_(negocios_ids)
    ).order_by(Mensaje.created_at.desc()).all()
    
    # Crear diccionario de negocios para acceso rápido
    negocios_dict = {n.id: n for n in negocios}
    
    # Contar no leídos
    no_leidos = sum(1 for m in mensajes if not m.leido)
    
    return render_template(
        "mensajes.html",
        mensajes=mensajes,
        negocios=negocios_dict,
        no_leidos=no_leidos,
        sin_negocios=False
    )


@app.route("/panel/mensajes/<int:id>")
def ver_mensaje(id):
    """Ver un mensaje individual y marcarlo como leído"""
    if not owner_required():
        return redirect("/cuenta")
    
    mensaje = db.session.get(Mensaje, id)
    if not mensaje:
        return "Mensaje no encontrado", 404
    
    # Verificar que el mensaje pertenece a un negocio del dueño
    negocio = db.session.get(Negocio, mensaje.negocio_id)
    if not negocio or negocio.owner_id != session["user_id"]:
        return "No tenés permiso para ver este mensaje.", 403
    
    # Marcar como leído
    if not mensaje.leido:
        mensaje.leido = True
        mensaje.updated_at = datetime.utcnow()
        db.session.commit()
    
    return render_template("ver_mensaje.html", mensaje=mensaje, negocio=negocio)


@app.route("/panel/mensajes/<int:id>/responder", methods=["POST"])
def responder_mensaje(id):
    """Responder a un mensaje por email"""
    if not owner_required():
        return redirect("/cuenta")
    
    mensaje = db.session.get(Mensaje, id)
    if not mensaje:
        return "Mensaje no encontrado", 404
    
    # Verificar que el mensaje pertenece a un negocio del dueño
    negocio = db.session.get(Negocio, mensaje.negocio_id)
    if not negocio or negocio.owner_id != session["user_id"]:
        return "No tenés permiso para responder este mensaje.", 403
    
    respuesta = (request.form.get("respuesta") or "").strip()
    if not respuesta or len(respuesta) < 10:
        flash("La respuesta debe tener al menos 10 caracteres.")
        return redirect(f"/panel/mensajes/{id}")
    
    # Obtener datos del dueño
    owner = db.session.get(Usuario, session["user_id"])
    
    try:
        base_url = get_base_url_from_request()
        negocio_url = f"{base_url}/negocio/{negocio.id}"
        
        text_body = (
            f"Hola {mensaje.nombre_remitente},\n\n"
            f"Recibiste una respuesta sobre tu mensaje enviado a '{negocio.nombre}'.\n\n"
            f"Tu mensaje original:\nAsunto: {mensaje.asunto}\n{mensaje.mensaje}\n\n"
            f"Respuesta:\n{respuesta}\n\n"
            f"Ver el negocio: {negocio_url}\n\n"
            f"Saludos,\n{owner.nombre or 'El equipo de Ubik2CR'}\n"
            f"Negocio: {negocio.nombre}"
        )
        
        html_body = f"""
        <div style="font-family:Arial,sans-serif;background:#f5f7fa;padding:24px">
            <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e6e8ee">
                <div style="background:linear-gradient(90deg,#0b4fa3,#38b24d);color:#fff;padding:18px 20px">
                    <div style="font-size:18px;font-weight:800">Ubik2CR</div>
                    <div style="opacity:.9;font-size:13px;margin-top:4px">Respuesta a tu mensaje</div>
                </div>
                <div style="padding:18px 20px;color:#111827">
                    <p style="margin:0 0 10px 0">Hola {mensaje.nombre_remitente},</p>
                    <p style="margin:0 0 14px 0;line-height:1.5">
                        Recibiste una respuesta sobre tu mensaje enviado a <b>{negocio.nombre}</b>.
                    </p>
                    <div style="background:#f9fafb;padding:15px;border-radius:10px;margin:15px 0">
                        <div style="margin-bottom:15px;padding-bottom:15px;border-bottom:1px solid #e5e7eb">
                            <strong style="color:#6b7280;font-size:12px">Tu mensaje original:</strong>
                            <div style="color:#111827;margin-top:5px">
                                <div style="font-weight:600;margin-bottom:5px">{mensaje.asunto}</div>
                                <div style="white-space:pre-wrap;line-height:1.5;color:#6b7280">{mensaje.mensaje}</div>
                            </div>
                        </div>
                        <div>
                            <strong style="color:#6b7280;font-size:12px">Respuesta:</strong>
                            <div style="color:#111827;margin-top:5px;white-space:pre-wrap;line-height:1.5;background:#fff;padding:10px;border-radius:5px;border-left:3px solid #0b4fa3">{respuesta}</div>
                        </div>
                    </div>
                    <div style="text-align:center;margin:18px 0">
                        <a href="{negocio_url}" style="display:inline-block;background:#0b4fa3;color:#fff;text-decoration:none;padding:12px 16px;border-radius:10px;font-weight:700">
                            Ver el Negocio
                        </a>
                    </div>
                    <p style="margin:15px 0 0 0;font-size:13px;color:#6b7280;line-height:1.5">
                        Saludos,<br>
                        <strong>{owner.nombre or 'El equipo de Ubik2CR'}</strong><br>
                        Negocio: {negocio.nombre}
                    </p>
                </div>
            </div>
            <div style="max-width:520px;margin:10px auto 0 auto;font-size:12px;color:#6b7280;text-align:center">
                © {datetime.now().year} Ubik2CR
            </div>
        </div>
        """
        
        send_email(mensaje.email_remitente, f"Respuesta sobre tu mensaje a '{negocio.nombre}'", text_body, html_body)
        
        # Marcar como respondido
        mensaje.respondido = True
        mensaje.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash("¡Respuesta enviada exitosamente!")
    except Exception as e:
        print(f"[EMAIL ERROR] No se pudo enviar respuesta a {mensaje.email_remitente}: {e}")
        flash("Error al enviar la respuesta. Por favor, intentá nuevamente.")
    
    return redirect(f"/panel/mensajes/{id}")


@app.route("/panel/mensajes/<int:id>/marcar-leido", methods=["POST"])
def marcar_mensaje_leido(id):
    """Marcar un mensaje como leído/no leído"""
    if not owner_required():
        return redirect("/cuenta")
    
    mensaje = db.session.get(Mensaje, id)
    if not mensaje:
        return "Mensaje no encontrado", 404
    
    # Verificar que el mensaje pertenece a un negocio del dueño
    negocio = db.session.get(Negocio, mensaje.negocio_id)
    if not negocio or negocio.owner_id != session["user_id"]:
        return "No tenés permiso para modificar este mensaje.", 403
    
    mensaje.leido = not mensaje.leido
    mensaje.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect("/panel/mensajes")


# =====================================================
# OWNER AUTH (DUEÑOS)
# =====================================================
@app.route("/owner/registro", methods=["GET", "POST"])
def owner_registro():
    if request.method == "POST":
        try:
            email = (request.form.get("email") or "").strip().lower()
            password = (request.form.get("password") or "").strip()
            nombre = (request.form.get("nombre") or "").strip()

            if not email or not password:
                flash("Por favor ingresá email y contraseña.")
                return redirect("/owner/registro")

            # Verificar si el usuario ya existe
            existe = Usuario.query.filter_by(email=email).first()
            if existe:
                flash("Ese correo ya existe. Iniciá sesión.")
                return redirect("/owner/login")

            # Generar hash de contraseña
            pwd_hash = generate_password_hash(password)

            # Crear nuevo usuario con rol VENDEDOR (compatible con sistema de vehículos)
            nuevo = Usuario(
                email=email, 
                password=pwd_hash, 
                nombre=nombre if nombre else None,
                rol="VENDEDOR",  # Cambiado de "OWNER" a "VENDEDOR" para consistencia
                tipo_usuario="individual",
                agencia_id=None  # Sin agencia por defecto
            )
            db.session.add(nuevo)
            db.session.commit()

            # Iniciar sesión automáticamente
            session["user_id"] = nuevo.id
            session["user_email"] = nuevo.email
            session["user_rol"] = nuevo.rol

            flash("✅ Cuenta creada exitosamente. Ahora podés publicar tus vehículos.")
            return redirect("/panel")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[ERROR REGISTRO] {error_trace}")
            flash(f"Error al crear cuenta: {str(e)}. Por favor, intentá nuevamente o contactá soporte.")
            return redirect("/owner/registro")

    return render_template("owner_registro.html")

@app.route("/owner/login", methods=["GET", "POST"])
def owner_login():
    if request.method == "POST":
        try:
            email = (request.form.get("usuario") or request.form.get("email") or "").strip().lower()
            password = (request.form.get("password") or "").strip()

            if not email or not password:
                flash("Por favor ingresá email y contraseña.")
                return redirect("/owner/login")

            u = Usuario.query.filter_by(email=email).first()
            if not u:
                flash("No existe ese usuario. Verificá tu correo o creá una cuenta.")
                return redirect("/owner/login")

            if not normalize_password_check(u.password, password):
                flash("Contraseña incorrecta. Si la olvidaste, usá '¿Olvidaste tu contraseña?'.")
                return redirect("/owner/login")

            # Si venía en texto plano en algún momento, se actualiza a hash
            if not (u.password.startswith(("pbkdf2:", "scrypt:"))):
                u.password = generate_password_hash(password)
                db.session.commit()

            # Iniciar sesión
            session["user_id"] = u.id
            session["user_email"] = u.email
            session["user_rol"] = u.rol

            flash("✅ Sesión iniciada correctamente.")
            return redirect("/panel")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[ERROR LOGIN] {error_trace}")
            flash(f"Error al iniciar sesión: {str(e)}. Por favor, intentá nuevamente.")
            return redirect("/owner/login")

    return render_template("owner_login.html")

@app.route("/owner/logout")
def owner_logout():
    session.pop("user_id", None)
    session.pop("user_email", None)
    session.pop("user_rol", None)
    return redirect("/")


# =====================================================
# OWNER PANEL
# =====================================================
@app.route("/panel")
def panel_owner():
    """Panel de vendedor - Gestionar vehículos"""
    if not owner_logged_in():
        return redirect("/cuenta")
    
    # Intentar mostrar panel de vehículos
    if VEHICULOS_AVAILABLE and Vehiculo is not None:
        try:
            user_id = session["user_id"]
            vehiculos = Vehiculo.query.filter_by(owner_id=user_id).order_by(Vehiculo.created_at.desc()).all()
            
            total = len(vehiculos)
            aprobados = len([v for v in vehiculos if v.estado == "aprobado"])
            pendientes = len([v for v in vehiculos if v.estado == "pendiente"])
            destacados = len([v for v in vehiculos if (v.es_vip or v.destacado) and v.estado == "aprobado"])
            
            user_email = session.get("user_email", "Usuario")
            
            return render_template(
                "panel_vehiculos.html",
                vehiculos=vehiculos,
                total=total,
                aprobados=aprobados,
                pendientes=pendientes,
                destacados=destacados,
                user_email=user_email
            )
        except Exception as e:
            print(f"[ERROR PANEL] Error al cargar vehículos: {e}")
            # Continuar con panel antiguo si hay error
    
    # Panel antiguo para negocios (fallback)

    # Si por alguna razón el modelo no tiene owner_id todavía, evitamos crash
    if not hasattr(Negocio, "owner_id"):
        flash("Falta el campo owner_id en Negocio. Necesita migración.")
        return render_template("panel_owner.html", negocios=[], total=0, aprobados=0, pendientes=0, vip=0, ofertas=[], noticias=[], user_email=session.get("user_email"), mensajes_no_leidos=0, ahora=datetime.utcnow())

    negocios = (
        Negocio.query.filter_by(owner_id=session["user_id"])
        .order_by(Negocio.id.desc())
        .all()
    )

    total = len(negocios)
    aprobados = len([n for n in negocios if n.estado == "aprobado"])
    pendientes = len([n for n in negocios if n.estado == "pendiente"])
    vip = len([n for n in negocios if n.es_vip and n.estado == "aprobado"])

    # Obtener ofertas de los negocios del dueño
    negocios_ids = [n.id for n in negocios]
    ofertas = Oferta.query.filter(Oferta.negocio_id.in_(negocios_ids)).order_by(Oferta.created_at.desc()).all() if negocios_ids else []
    
    # Obtener noticias de los negocios del dueño
    noticias = Noticia.query.filter(Noticia.negocio_id.in_(negocios_ids)).order_by(Noticia.fecha.desc()).all() if negocios_ids else []
    
    # Obtener mensajes no leídos
    mensajes_no_leidos = 0
    if negocios_ids:
        mensajes_no_leidos = Mensaje.query.filter(
            Mensaje.negocio_id.in_(negocios_ids),
            Mensaje.leido == False
        ).count()
    
    # Pasar datetime actual al template
    from datetime import datetime as dt
    ahora = dt.utcnow()
    
    return render_template(
        "panel_owner.html",
        negocios=negocios,
        total=total,
        aprobados=aprobados,
        pendientes=pendientes,
        vip=vip,
        ofertas=ofertas,
        noticias=noticias,
        user_email=session.get("user_email"),
        ahora=ahora,
        mensajes_no_leidos=mensajes_no_leidos,
    )

@app.route("/panel/negocio/<int:id>/editar", methods=["GET", "POST"])
def editar_negocio_owner(id):
    if not owner_required():
        return redirect("/cuenta")

    negocio = db.session.get(Negocio, id)
    if not negocio:
        return "Negocio no encontrado", 404

    if hasattr(negocio, "owner_id") and negocio.owner_id != session["user_id"]:
        return "No tenés permiso para editar este negocio.", 403

    if request.method == "POST":
        negocio.nombre = request.form.get("nombre", negocio.nombre)
        negocio.categoria = request.form.get("categoria", negocio.categoria)
        negocio.ubicacion = request.form.get("ubicacion", negocio.ubicacion)
        negocio.provincia = request.form.get("provincia", "").strip() or None
        negocio.canton = request.form.get("canton", "").strip() or None
        negocio.distrito = request.form.get("distrito", "").strip() or None
        negocio.descripcion = request.form.get("descripcion", negocio.descripcion)
        negocio.telefono = request.form.get("telefono", negocio.telefono)
        negocio.whatsapp = request.form.get("whatsapp", negocio.whatsapp)
        # Horario
        negocio.abierto_24h = bool(request.form.get("abierto_24h"))
        if negocio.abierto_24h:
            negocio.horario = None  # Si está 24h, no guardar horario específico
        else:
            try:
                horario_parsed = parse_horario_from_form(request.form)
                # Solo guardar si hay al menos un día abierto
                horario_dict = json.loads(horario_parsed) if horario_parsed else {}
                tiene_dias_abiertos = any(dia.get("abierto", False) for dia in horario_dict.values())
                if tiene_dias_abiertos:
                    negocio.horario = horario_parsed
                else:
                    negocio.horario = None  # Si no hay días marcados, dejar None
            except Exception as e:
                print(f"[ERROR] Error al parsear horario: {e}")
                negocio.horario = None  # En caso de error, dejar None
        negocio.maps_url = request.form.get("maps_url", negocio.maps_url)
        
        # Procesar productos_tags (opcional)
        productos_tags_str = request.form.get("productos_tags_json", "").strip()
        if productos_tags_str:
            try:
                productos_tags_list = json.loads(productos_tags_str)
                if productos_tags_list and isinstance(productos_tags_list, list):
                    negocio.productos_tags = json.dumps([tag.lower().strip() for tag in productos_tags_list if tag.strip()])
                else:
                    negocio.productos_tags = None
            except:
                # Fallback: procesar como string separado por comas
                productos_tags_raw = request.form.get("productos_tags", "").strip()
                if productos_tags_raw:
                    productos_tags_list = [tag.lower().strip() for tag in productos_tags_raw.split(",") if tag.strip()]
                    negocio.productos_tags = json.dumps(productos_tags_list) if productos_tags_list else None
                else:
                    negocio.productos_tags = None
        else:
            # Si no viene nada, limpiar
            negocio.productos_tags = None

        negocio.latitud = safe_float(request.form.get("latitud"))
        negocio.longitud = safe_float(request.form.get("longitud"))

        img = request.files.get("foto")
        if img and img.filename:
            negocio.imagen_url = save_upload("foto")

        # Cada edición vuelve a pendiente para revisión
        negocio.estado = "pendiente"

        db.session.commit()
        flash("Cambios guardados. Quedó pendiente de revisión.")
        return redirect("/panel")

    return render_template(
        "editar_negocio.html", 
        n=negocio,
        get_horario_dict=get_horario_dict
    )

@app.route("/panel/negocio/<int:id>/ceder", methods=["GET", "POST"])
def ceder_negocio(id):
    """Ceder un negocio a otro usuario por email"""
    if not owner_required():
        return redirect("/cuenta")

    negocio = db.session.get(Negocio, id)
    if not negocio:
        return "Negocio no encontrado", 404

    if hasattr(negocio, "owner_id") and negocio.owner_id != session["user_id"]:
        return "No tenés permiso para ceder este negocio.", 403

    if request.method == "POST":
        nuevo_owner_email = (request.form.get("email") or "").strip().lower()
        
        if not nuevo_owner_email:
            flash("Debés ingresar un correo electrónico.")
            return redirect(f"/panel/negocio/{id}/ceder")
        
        # Buscar el usuario por email
        nuevo_owner = Usuario.query.filter_by(email=nuevo_owner_email).first()
        
        if not nuevo_owner:
            flash(f"No existe un usuario con el correo {nuevo_owner_email}. El usuario debe estar registrado en Ubik2CR.")
            return redirect(f"/panel/negocio/{id}/ceder")
        
        if nuevo_owner.id == session["user_id"]:
            flash("No podés ceder el negocio a vos mismo.")
            return redirect(f"/panel/negocio/{id}/ceder")
        
        # Guardar datos para el email
        antiguo_owner_email = session.get("user_email")
        antiguo_owner_nombre = Usuario.query.get(session["user_id"]).nombre or "Dueño anterior"
        negocio_nombre = negocio.nombre
        nuevo_owner_nombre = nuevo_owner.nombre or nuevo_owner.email
        
        # Transferir el negocio
        negocio.owner_id = nuevo_owner.id
        db.session.commit()
        
        # Enviar email de notificación al nuevo dueño (en segundo plano)
        base_url = get_base_url_from_request()
        negocio_url = f"{base_url}/negocio/{negocio.id}"
        
        text_body = (
            f"Hola {nuevo_owner_nombre},\n\n"
            f"¡Felicidades! El negocio '{negocio_nombre}' te ha sido cedido por {antiguo_owner_nombre}.\n\n"
            f"Ahora sos el dueño de este negocio en Ubik2CR.\n\n"
            f"Podés verlo y administrarlo aquí: {negocio_url}\n\n"
            f"Accedé a tu panel para gestionarlo: {base_url}/panel\n\n"
            f"Saludos,\n"
            f"El equipo de Ubik2CR"
        )
        
        html_body = f"""
        <div style="font-family:Arial,sans-serif;background:#f5f7fa;padding:24px">
            <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e6e8ee">
                <div style="background:linear-gradient(90deg,#0b4fa3,#38b24d);color:#fff;padding:18px 20px">
                    <div style="font-size:18px;font-weight:800">Ubik2CR</div>
                    <div style="opacity:.9;font-size:13px;margin-top:4px">Negocio Cedido</div>
                </div>
                <div style="padding:18px 20px;color:#111827">
                    <p style="margin:0 0 10px 0">Hola {nuevo_owner_nombre},</p>
                    <p style="margin:0 0 14px 0;line-height:1.5">
                        ¡Felicidades! El negocio <strong>"{negocio_nombre}"</strong> te ha sido cedido por <strong>{antiguo_owner_nombre}</strong>.
                    </p>
                    <p style="margin:0 0 14px 0;line-height:1.5">
                        Ahora sos el dueño de este negocio en Ubik2CR y podés administrarlo desde tu panel.
                    </p>
                    <div style="text-align:center;margin:18px 0">
                        <a href="{negocio_url}" style="display:inline-block;background:#0b4fa3;color:#fff;text-decoration:none;padding:12px 16px;border-radius:10px;font-weight:700;margin-right:10px">
                            Ver negocio
                        </a>
                        <a href="{base_url}/panel" style="display:inline-block;background:#38b24d;color:#fff;text-decoration:none;padding:12px 16px;border-radius:10px;font-weight:700">
                            Ir a mi panel
                        </a>
                    </div>
                </div>
            </div>
            <div style="max-width:520px;margin:10px auto 0 auto;font-size:12px;color:#6b7280;text-align:center">
                © {datetime.now().year} Ubik2CR
            </div>
        </div>
        """
        
        def enviar_email_background():
            try:
                send_email(
                    nuevo_owner_email,
                    f"¡Te han cedido el negocio '{negocio_nombre}' en Ubik2CR!",
                    text_body,
                    html_body
                )
                print(f"[NOTIFICACION] Email enviado a {nuevo_owner_email} - Negocio cedido: {negocio_nombre}")
            except Exception as e:
                print(f"[NOTIFICACION][ERROR] No se pudo enviar email a {nuevo_owner_email}: {repr(e)}")
        
        # Enviar email en segundo plano
        thread = threading.Thread(target=enviar_email_background)
        thread.daemon = True
        thread.start()
        
        flash(f"¡Negocio '{negocio_nombre}' cedido exitosamente a {nuevo_owner_nombre} ({nuevo_owner_email})!")
        return redirect("/panel")
    
    return render_template("ceder_negocio.html", negocio=negocio)


# =====================================================
# PUBLICAR NEGOCIO (solo dueño logueado)
# =====================================================
@app.route("/publicar", methods=["GET", "POST"])
def publicar():
    if not owner_required():
        flash("Creá tu cuenta o iniciá sesión para publicar tu negocio.")
        return redirect("/cuenta")

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        telefono = request.form.get("telefono")
        whatsapp = request.form.get("whatsapp")
        # Horario
        abierto_24h = bool(request.form.get("abierto_24h"))
        if abierto_24h:
            horario = None  # Si está 24h, no guardar horario específico
        else:
            horario = parse_horario_from_form(request.form)
        maps_url = request.form.get("maps_url")

        latitud = safe_float(request.form.get("latitud"))
        longitud = safe_float(request.form.get("longitud"))

        # Guardar múltiples imágenes (hasta 10) - UNA SOLA VEZ
        fotos_urls = save_multiple_uploads("fotos", max_files=10)
        # La primera foto será la imagen principal
        imagen_url = fotos_urls[0] if fotos_urls else "/static/uploads/logo.png"
        
        # Procesar productos_tags (opcional)
        productos_tags_json = None
        productos_tags_str = request.form.get("productos_tags_json", "").strip()
        if productos_tags_str:
            try:
                productos_tags_list = json.loads(productos_tags_str)
                if productos_tags_list and isinstance(productos_tags_list, list):
                    productos_tags_json = json.dumps([tag.lower().strip() for tag in productos_tags_list if tag.strip()])
            except:
                # Fallback: procesar como string separado por comas
                productos_tags_raw = request.form.get("productos_tags", "").strip()
                if productos_tags_raw:
                    productos_tags_list = [tag.lower().strip() for tag in productos_tags_raw.split(",") if tag.strip()]
                    if productos_tags_list:
                        productos_tags_json = json.dumps(productos_tags_list)

        # Obtener ubicación geográfica
        provincia = request.form.get("provincia", "").strip()
        canton = request.form.get("canton", "").strip()
        distrito = request.form.get("distrito", "").strip()
        
        nuevo_negocio = Negocio(
            nombre=nombre,
            categoria=categoria,
            ubicacion=ubicacion,
            provincia=provincia if provincia else None,
            canton=canton if canton else None,
            distrito=distrito if distrito else None,
            latitud=latitud,
            longitud=longitud,
            maps_url=maps_url,
            telefono=telefono,
            whatsapp=whatsapp,
            horario=horario,
            abierto_24h=abierto_24h,
            descripcion=descripcion,
            imagen_url=imagen_url,
            productos_tags=productos_tags_json,
            estado="pendiente",
            es_vip=False,
        )

        # Si existe owner_id en el modelo, lo asignamos
        if hasattr(Negocio, "owner_id"):
            setattr(nuevo_negocio, "owner_id", session["user_id"])

        db.session.add(nuevo_negocio)
        db.session.flush()  # Para obtener el ID del negocio
        
        # Guardar las imágenes en la tabla imagenes_negocio (si la tabla existe)
        # Si la migración no se ha ejecutado, solo guardamos la imagen principal
        try:
            if fotos_urls:
                for orden, foto_url in enumerate(fotos_urls):
                    imagen_negocio = ImagenNegocio(
                        negocio_id=nuevo_negocio.id,
                        imagen_url=foto_url,
                        orden=orden
                    )
                    db.session.add(imagen_negocio)
        except Exception as e:
            # Si la tabla imagenes_negocio no existe, solo continuamos con la imagen principal
            print(f"[IMAGENES] No se pudieron guardar imágenes adicionales: {e}")
        
        db.session.commit()
        # Pasar información de sesión para mostrar botón condicional
        user_logged_in = "user_id" in session
        return render_template("exito.html", user_logged_in=user_logged_in)

    return render_template("registro.html")


# =====================================================
# PUBLICAR VEHÍCULOS
# =====================================================
@app.route("/vehiculos/publicar", methods=["GET", "POST"])
def publicar_vehiculo():
    """Publicar un vehículo nuevo"""
    if not VEHICULOS_AVAILABLE:
        flash("El sistema de vehículos está en proceso de configuración. Por favor, ejecutá las migraciones primero.")
        return redirect("/")
    
    # Verificar si el usuario está logueado
    if "user_id" not in session:
        flash("Creá tu cuenta o iniciá sesión para publicar tu vehículo.")
        return redirect("/cuenta")
    
    # Verificar que las tablas existen
    try:
        Vehiculo.query.limit(1).all()
    except Exception as e:
        print(f"[ERROR] Tabla de vehículos no existe aún: {e}")
        flash("El sistema de vehículos está en proceso de configuración. Por favor, ejecutá: flask db upgrade")
        return redirect("/")
    
    if request.method == "POST":
        # Obtener datos del formulario
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        año_str = request.form.get("año", "").strip()
        precio_str = request.form.get("precio", "").strip()
        kilometraje_str = request.form.get("kilometraje", "").strip()
        tipo_vehiculo = request.form.get("tipo_vehiculo", "").strip()
        transmision = request.form.get("transmision", "").strip() or None
        combustible = request.form.get("combustible", "").strip() or None
        color = request.form.get("color", "").strip() or None
        estado_vehiculo = request.form.get("estado_vehiculo", "Usado").strip()
        descripcion = request.form.get("descripcion", "").strip()
        provincia = request.form.get("provincia", "").strip() or None
        canton = request.form.get("canton", "").strip() or None
        distrito = request.form.get("distrito", "").strip() or None
        telefono = request.form.get("telefono", "").strip() or None
        whatsapp = request.form.get("whatsapp", "").strip() or None
        
        # Validaciones
        if not marca or not modelo or not año_str or not precio_str or not descripcion:
            flash("Completá todos los campos obligatorios.")
            return redirect("/vehiculos/publicar")
        
        try:
            año = int(año_str)
            if año < 1950 or año > 2025:
                flash("El año debe estar entre 1950 y 2025.")
                return redirect("/vehiculos/publicar")
        except ValueError:
            flash("El año debe ser un número válido.")
            return redirect("/vehiculos/publicar")
        
        try:
            precio = float(precio_str)
            if precio < 0:
                flash("El precio no puede ser negativo.")
                return redirect("/vehiculos/publicar")
        except ValueError:
            flash("El precio debe ser un número válido.")
            return redirect("/vehiculos/publicar")
        
        kilometraje = None
        if kilometraje_str:
            try:
                kilometraje = int(kilometraje_str)
                if kilometraje < 0:
                    flash("El kilometraje no puede ser negativo.")
                    return redirect("/vehiculos/publicar")
            except ValueError:
                pass  # Si no es válido, dejarlo como None
        
        # Guardar imágenes (hasta 10)
        imagenes_urls = save_multiple_uploads("imagenes", max_files=10)
        imagen_url = imagenes_urls[0] if imagenes_urls else "/static/uploads/logo.png"
        
        # Crear vehículo
        nuevo_vehiculo = Vehiculo(
            owner_id=session["user_id"],
            marca=marca,
            modelo=modelo,
            año=año,
            precio=precio,
            kilometraje=kilometraje,
            tipo_vehiculo=tipo_vehiculo,
            transmision=transmision,
            combustible=combustible,
            color=color,
            estado_vehiculo=estado_vehiculo,
            descripcion=descripcion,
            provincia=provincia,
            canton=canton,
            distrito=distrito,
            telefono=telefono,
            whatsapp=whatsapp,
            imagen_url=imagen_url,
            estado="pendiente",
            es_vip=False,
            destacado=False
        )
        
        db.session.add(nuevo_vehiculo)
        db.session.flush()  # Para obtener el ID
        
        # Guardar imágenes adicionales en la tabla ImagenVehiculo
        try:
            for orden, img_url in enumerate(imagenes_urls[1:], start=1):  # Empezar desde la segunda imagen
                imagen_vehiculo = ImagenVehiculo(
                    vehiculo_id=nuevo_vehiculo.id,
                    imagen_url=img_url,
                    orden=orden
                )
                db.session.add(imagen_vehiculo)
        except Exception as e:
            print(f"[IMAGENES] No se pudieron guardar imágenes adicionales: {e}")
        
        db.session.commit()
        
        flash("¡Vehículo publicado exitosamente! Está pendiente de aprobación.")
        return redirect("/panel")
    
    # GET: Mostrar formulario
    # Cargar datos de ubicaciones
    import os
    json_path = os.path.join(os.path.dirname(__file__), "static", "data", "costa_rica_ubicaciones.json")
    ubicaciones_data = {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            ubicaciones_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar ubicaciones: {e}")
    
    return render_template("vehiculos_publicar.html", ubicaciones_data=ubicaciones_data)


@app.route("/vehiculo/<int:vehiculo_id>")
def detalle_vehiculo(vehiculo_id):
    """Página de detalle de un vehículo"""
    if not VEHICULOS_AVAILABLE:
        flash("El sistema de vehículos aún no está disponible.")
        return redirect("/")
    
    try:
        vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
        
        # Solo mostrar vehículos aprobados (o si es el dueño/admin)
        if vehiculo.estado != "aprobado":
            if "user_id" not in session or (vehiculo.owner_id != session["user_id"] and not admin_logged_in()):
                flash("Este vehículo no está disponible.")
                return redirect("/")
        
        # Obtener imágenes adicionales
        imagenes_adicionales = []
        try:
            imagenes_adicionales = ImagenVehiculo.query.filter_by(
                vehiculo_id=vehiculo_id
            ).order_by(ImagenVehiculo.orden).all()
        except Exception as e:
            print(f"[ERROR] No se pudieron cargar imágenes adicionales: {e}")
        
        return render_template(
            "vehiculo_detalle.html",
            vehiculo=vehiculo,
            imagenes_adicionales=imagenes_adicionales
        )
    except Exception as e:
        print(f"[ERROR] Error al cargar detalle de vehículo: {e}")
        flash("Error al cargar el vehículo. Por favor, intentá más tarde.")
        return redirect("/")


@app.route("/panel/vehiculo/<int:vehiculo_id>/marcar-vendido", methods=["POST"])
def marcar_vehiculo_vendido(vehiculo_id):
    """Marcar un vehículo como vendido"""
    if not VEHICULOS_AVAILABLE:
        flash("El sistema de vehículos no está disponible.")
        return redirect("/panel")
    
    if "user_id" not in session:
        flash("Debés iniciar sesión.")
        return redirect("/cuenta")
    
    try:
        vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
        
        # Verificar que el vehículo pertenece al usuario
        if vehiculo.owner_id != session["user_id"]:
            flash("No tenés permiso para modificar este vehículo.")
            return redirect("/panel")
        
        vehiculo.estado = "vendido"
        vehiculo.fecha_venta = datetime.utcnow()
        db.session.commit()
        
        flash("¡Vehículo marcado como vendido!")
        return redirect("/panel")
    except Exception as e:
        print(f"[ERROR] Error al marcar vehículo como vendido: {e}")
        flash("Error al actualizar el vehículo.")
        return redirect("/panel")


@app.route("/panel/vehiculo/<int:vehiculo_id>/eliminar", methods=["POST"])
def eliminar_vehiculo(vehiculo_id):
    """Eliminar un vehículo"""
    if not VEHICULOS_AVAILABLE:
        flash("El sistema de vehículos no está disponible.")
        return redirect("/panel")
    
    if "user_id" not in session:
        flash("Debés iniciar sesión.")
        return redirect("/cuenta")
    
    try:
        vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
        
        # Verificar que el vehículo pertenece al usuario
        if vehiculo.owner_id != session["user_id"]:
            flash("No tenés permiso para eliminar este vehículo.")
            return redirect("/panel")
        
        # Eliminar imágenes asociadas
        try:
            ImagenVehiculo.query.filter_by(vehiculo_id=vehiculo_id).delete()
        except Exception as e:
            print(f"[ERROR] No se pudieron eliminar imágenes: {e}")
        
        db.session.delete(vehiculo)
        db.session.commit()
        
        flash("Vehículo eliminado exitosamente.")
        return redirect("/panel")
    except Exception as e:
        print(f"[ERROR] Error al eliminar vehículo: {e}")
        flash("Error al eliminar el vehículo.")
        return redirect("/panel")


# =====================================================
# GESTIONAR OFERTAS (DUEÑOS)
# =====================================================
@app.route("/panel/oferta/nueva", methods=["GET", "POST"])
def crear_oferta():
    """Crear una nueva oferta"""
    if not owner_required():
        return redirect("/cuenta")
    
    if request.method == "POST":
        negocio_id = int(request.form.get("negocio_id", 0))
        titulo = (request.form.get("titulo") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        fecha_caducidad_str = (request.form.get("fecha_caducidad") or "").strip()
        
        # Validar que el negocio pertenece al dueño
        negocio = db.session.get(Negocio, negocio_id)
        if not negocio or negocio.owner_id != session["user_id"]:
            flash("No tenés permiso para crear ofertas en ese negocio.")
            return redirect("/panel")
        
        if not titulo or not fecha_caducidad_str:
            flash("Título y fecha de caducidad son obligatorios.")
            return redirect("/panel/oferta/nueva")
        
        try:
            fecha_caducidad = datetime.strptime(fecha_caducidad_str, "%Y-%m-%d")
        except ValueError:
            flash("Fecha de caducidad inválida.")
            return redirect("/panel/oferta/nueva")
        
        # Validar que no exceda 2 meses
        from datetime import timedelta
        ahora = datetime.utcnow()
        dos_meses_despues = ahora + timedelta(days=60)  # Aproximadamente 2 meses
        
        if fecha_caducidad > dos_meses_despues:
            flash("La fecha de caducidad no puede ser mayor a 2 meses desde hoy.")
            return redirect("/panel/oferta/nueva")
        
        if fecha_caducidad <= ahora:
            flash("La fecha de caducidad debe ser mayor a hoy.")
            return redirect("/panel/oferta/nueva")
        
        # Guardar imagen
        imagen_url = save_upload("imagen")
        if not imagen_url or imagen_url == "/static/uploads/logo.png":
            flash("Debés subir una imagen para la oferta.")
            return redirect("/panel/oferta/nueva")
        
        nueva_oferta = Oferta(
            negocio_id=negocio_id,
            titulo=titulo,
            descripcion=descripcion,
            imagen_url=imagen_url,
            fecha_caducidad=fecha_caducidad,
            estado="activa"
        )
        
        db.session.add(nueva_oferta)
        db.session.commit()
        
        flash("¡Oferta creada exitosamente!")
        return redirect("/panel")
    
    # GET: mostrar formulario
    negocios = Negocio.query.filter_by(
        owner_id=session["user_id"],
        estado="aprobado"
    ).all()
    
    return render_template("crear_oferta.html", negocios=negocios)

@app.route("/panel/oferta/<int:id>/editar", methods=["GET", "POST"])
def editar_oferta(id):
    """Editar una oferta existente"""
    if not owner_required():
        return redirect("/cuenta")
    
    oferta = db.session.get(Oferta, id)
    if not oferta:
        return "Oferta no encontrada", 404
    
    # Validar que el negocio pertenece al dueño
    negocio = db.session.get(Negocio, oferta.negocio_id)
    if not negocio or negocio.owner_id != session["user_id"]:
        return "No tenés permiso para editar esta oferta.", 403
    
    if request.method == "POST":
        oferta.titulo = (request.form.get("titulo") or "").strip()
        oferta.descripcion = (request.form.get("descripcion") or "").strip()
        fecha_caducidad_str = (request.form.get("fecha_caducidad") or "").strip()
        
        if fecha_caducidad_str:
            try:
                fecha_caducidad = datetime.strptime(fecha_caducidad_str, "%Y-%m-%d")
                
                # Validar que no exceda 2 meses desde la fecha de inicio
                from datetime import timedelta
                dos_meses_despues = oferta.fecha_inicio + timedelta(days=60)  # Aproximadamente 2 meses
                
                if fecha_caducidad > dos_meses_despues:
                    flash("La fecha de caducidad no puede ser mayor a 2 meses desde la fecha de inicio.")
                    return redirect(f"/panel/oferta/{id}/editar")
                
                oferta.fecha_caducidad = fecha_caducidad
            except ValueError:
                flash("Fecha de caducidad inválida.")
                return redirect(f"/panel/oferta/{id}/editar")
        
        # Actualizar imagen si se sube una nueva
        img = request.files.get("imagen")
        if img and img.filename:
            oferta.imagen_url = save_upload("imagen")
        
        db.session.commit()
        flash("Oferta actualizada.")
        return redirect("/panel")
    
    return render_template("editar_oferta.html", oferta=oferta)

@app.route("/panel/oferta/<int:id>/eliminar")
def eliminar_oferta(id):
    """Eliminar una oferta"""
    if not owner_required():
        return redirect("/cuenta")
    
    oferta = db.session.get(Oferta, id)
    if not oferta:
        return "Oferta no encontrada", 404
    
    # Validar que el negocio pertenece al dueño
    negocio = db.session.get(Negocio, oferta.negocio_id)
    if not negocio or negocio.owner_id != session["user_id"]:
        return "No tenés permiso para eliminar esta oferta.", 403
    
    db.session.delete(oferta)
    db.session.commit()
    
    flash("Oferta eliminada.")
    return redirect("/panel")


# =====================================================
# ADMIN AUTH (PLATAFORMA)
# =====================================================
@app.route("/login", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        user = (request.form.get("usuario") or "").strip()
        password = (request.form.get("password") or "").strip()

        admin_user = (os.environ.get("ADMIN_USER") or "").strip()
        admin_pass = (os.environ.get("ADMIN_PASS") or "").strip()

        if user == admin_user and password == admin_pass:
            session["admin_logged_in"] = True
            return redirect("/admin")

        flash("Datos incorrectos. Verifica tu correo y contraseña.")

    return render_template("login.html")

@app.route("/logout")
def logout_admin():
    session.clear()
    return redirect("/")


# =====================================================
# ADMIN PANEL
# =====================================================
@app.route("/admin")
def admin_panel():
    if not admin_logged_in():
        return redirect("/login")

    # Estadísticas para sistema de vehículos (si existe)
    total_vehiculos_pendientes = 0
    total_vehiculos_aprobados = 0
    total_agencias_pendientes = 0
    total_agencias_aprobadas = 0
    
    if VEHICULOS_AVAILABLE:
        if Vehiculo is not None:
            try:
                total_vehiculos_pendientes = Vehiculo.query.filter_by(estado="pendiente").count()
                total_vehiculos_aprobados = Vehiculo.query.filter_by(estado="aprobado").count()
            except:
                pass
        
        if Agencia is not None:
            try:
                total_agencias_pendientes = Agencia.query.filter_by(estado="pendiente").count()
                total_agencias_aprobadas = Agencia.query.filter_by(estado="aprobado").count()
            except:
                pass

    return render_template("dashboard.html", 
                         vehiculos_pendientes=total_vehiculos_pendientes,
                         vehiculos_aprobados=total_vehiculos_aprobados,
                         agencias_pendientes=total_agencias_pendientes,
                         agencias_aprobadas=total_agencias_aprobadas)

@app.route("/admin/vehiculos")
def gestionar_vehiculos():
    """Gestionar vehículos pendientes y aprobados"""
    if not admin_logged_in():
        return redirect("/login")
    
    if not VEHICULOS_AVAILABLE or Vehiculo is None:
        flash("El sistema de vehículos aún no está disponible. Ejecutá las migraciones primero.")
        return redirect("/admin")
    
    try:
        pendientes = Vehiculo.query.filter_by(estado="pendiente").order_by(Vehiculo.id.desc()).all()
        aprobados = Vehiculo.query.filter_by(estado="aprobado").order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.id.desc()).all()
        vendidos = Vehiculo.query.filter_by(estado="vendido").order_by(Vehiculo.id.desc()).all()
        
        return render_template("admin_vehiculos.html", 
                             pendientes=pendientes, 
                             aprobados=aprobados,
                             vendidos=vendidos)
    except Exception as e:
        print(f"[ERROR ADMIN VEHICULOS] {e}")
        flash("Error al cargar vehículos. Verificá que las tablas existan.")
        return redirect("/admin")

@app.route("/admin/agencias")
def gestionar_agencias():
    """Gestionar agencias pendientes y aprobadas"""
    if not admin_logged_in():
        return redirect("/login")
    
    if not VEHICULOS_AVAILABLE or Agencia is None:
        flash("El sistema de agencias aún no está disponible. Ejecutá las migraciones primero.")
        return redirect("/admin")
    
    try:
        pendientes = Agencia.query.filter_by(estado="pendiente").order_by(Agencia.id.desc()).all()
        aprobadas = Agencia.query.filter_by(estado="aprobado").order_by(Agencia.es_vip.desc(), Agencia.id.desc()).all()
        
        return render_template("admin_agencias.html", 
                             pendientes=pendientes, 
                             aprobadas=aprobadas)
    except Exception as e:
        print(f"[ERROR ADMIN AGENCIAS] {e}")
        flash("Error al cargar agencias. Verificá que las tablas existan.")
        return redirect("/admin")

# DEPRECATED: Mantener por compatibilidad pero redirigir a vehículos
@app.route("/admin/comercios")
def gestionar_comercios():
    """DEPRECATED: Redirigir a gestión de vehículos"""
    if not admin_logged_in():
        return redirect("/login")
    return redirect("/admin/vehiculos")

@app.route("/admin/aprobar/<int:id>")
def aprobar_negocio(id):
    if not admin_logged_in():
        return redirect("/login")

    negocio = db.session.get(Negocio, id)
    if negocio:
        negocio.estado = "aprobado"
        db.session.commit()
        
        # Enviar email de notificación al dueño EN SEGUNDO PLANO (no bloquea)
        if hasattr(negocio, "owner_id") and negocio.owner_id:
            owner = db.session.get(Usuario, negocio.owner_id)
            if owner and owner.email:
                # Preparar datos para el email (antes de crear el hilo)
                base_url = get_base_url_from_request()
                negocio_url = f"{base_url}/negocio/{negocio.id}"
                negocio_nombre = negocio.nombre
                owner_nombre = owner.nombre or 'dueño del negocio'
                owner_email = owner.email
                
                text_body = (
                    f"Hola {owner_nombre},\n\n"
                    f"¡Excelentes noticias! Tu negocio '{negocio_nombre}' ha sido aprobado y ya está visible en Ubik2CR.\n\n"
                    f"Puedes verlo aquí: {negocio_url}\n\n"
                    f"Gracias por ser parte de Ubik2CR.\n\n"
                    f"Saludos,\n"
                    f"El equipo de Ubik2CR"
                )
                
                html_body = f"""
                <div style="font-family:Arial,sans-serif;background:#f5f7fa;padding:24px">
                    <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e6e8ee">
                        <div style="background:linear-gradient(90deg,#0b4fa3,#38b24d);color:#fff;padding:18px 20px">
                            <div style="font-size:18px;font-weight:800">Ubik2CR</div>
                            <div style="opacity:.9;font-size:13px;margin-top:4px">Tu negocio fue aprobado</div>
                        </div>
                        <div style="padding:18px 20px;color:#111827">
                            <p style="margin:0 0 10px 0">Hola {owner_nombre},</p>
                            <p style="margin:0 0 14px 0;line-height:1.5">
                                ¡Excelentes noticias! Tu negocio <strong>"{negocio_nombre}"</strong> ha sido aprobado y ya está visible en Ubik2CR.
                            </p>
                            <div style="text-align:center;margin:18px 0">
                                <a href="{negocio_url}" style="display:inline-block;background:#0b4fa3;color:#fff;text-decoration:none;padding:12px 16px;border-radius:10px;font-weight:700">
                                    Ver mi negocio
                                </a>
                            </div>
                            <p style="margin:0 0 10px 0;font-size:13px;opacity:.85;line-height:1.5">
                                Gracias por ser parte de Ubik2CR.
                            </p>
                        </div>
                    </div>
                    <div style="max-width:520px;margin:10px auto 0 auto;font-size:12px;color:#6b7280;text-align:center">
                        © {datetime.now().year} Ubik2CR
                    </div>
                </div>
                """
                
                # Enviar email en un hilo separado (no bloquea la respuesta)
                def enviar_email_background():
                    try:
                        send_email(
                            owner_email,
                            f"¡Tu negocio '{negocio_nombre}' fue aprobado! - Ubik2CR",
                            text_body,
                            html_body
                        )
                        print(f"[NOTIFICACION] Email enviado a {owner_email} - Negocio aprobado: {negocio_nombre}")
                    except Exception as e:
                        print(f"[NOTIFICACION][ERROR] No se pudo enviar email a {owner_email}: {repr(e)}")
                
                # Iniciar el hilo en segundo plano
                thread = threading.Thread(target=enviar_email_background)
                thread.daemon = True  # Se cierra cuando termina la app
                thread.start()

    return redirect("/admin/comercios")

@app.route("/admin/eliminar/<int:id>")
def eliminar_negocio(id):
    if not admin_logged_in():
        return redirect("/login")

    negocio = db.session.get(Negocio, id)
    if negocio:
        db.session.delete(negocio)
        db.session.commit()

    return redirect("/admin/comercios")

@app.route("/admin/vip/<int:id>")
def toggle_vip(id):
    if not admin_logged_in():
        return redirect("/login")

    n = db.session.get(Negocio, id)
    if n:
        n.es_vip = not bool(n.es_vip)
        db.session.commit()

    return redirect("/admin/comercios")

@app.route("/admin/editar/<int:id>", methods=["GET", "POST"])
def editar_negocio_admin(id):
    if not admin_logged_in():
        return redirect("/login")

    n = db.session.get(Negocio, id)
    if not n:
        return "Negocio no encontrado", 404

    if request.method == "POST":
        n.nombre = request.form.get("nombre", n.nombre)
        n.categoria = request.form.get("categoria", n.categoria)
        n.ubicacion = request.form.get("ubicacion", n.ubicacion)
        
        # Guardar ubicación geográfica (provincia, cantón, distrito)
        n.provincia = request.form.get("provincia", "").strip() or None
        n.canton = request.form.get("canton", "").strip() or None
        n.distrito = request.form.get("distrito", "").strip() or None
        
        n.descripcion = request.form.get("descripcion", n.descripcion)
        n.telefono = request.form.get("telefono", n.telefono)
        n.whatsapp = request.form.get("whatsapp", n.whatsapp)
        # Horario
        n.abierto_24h = bool(request.form.get("abierto_24h"))
        if n.abierto_24h:
            n.horario = None  # Si está 24h, no guardar horario específico
        else:
            try:
                horario_parsed = parse_horario_from_form(request.form)
                # Solo guardar si hay al menos un día abierto
                horario_dict = json.loads(horario_parsed) if horario_parsed else {}
                tiene_dias_abiertos = any(dia.get("abierto", False) for dia in horario_dict.values())
                if tiene_dias_abiertos:
                    n.horario = horario_parsed
                else:
                    n.horario = None  # Si no hay días marcados, dejar None
            except Exception as e:
                print(f"[ERROR] Error al parsear horario: {e}")
                n.horario = None  # En caso de error, dejar None
        n.maps_url = request.form.get("maps_url", n.maps_url)
        
        # Procesar productos_tags (opcional) - Solo si el campo existe en el modelo
        if hasattr(Negocio, 'productos_tags'):
            productos_tags_str = request.form.get("productos_tags_json", "").strip()
            if productos_tags_str:
                try:
                    productos_tags_list = json.loads(productos_tags_str)
                    if productos_tags_list and isinstance(productos_tags_list, list):
                        n.productos_tags = json.dumps([tag.lower().strip() for tag in productos_tags_list if tag.strip()])
                    else:
                        n.productos_tags = None
                except:
                    # Fallback: procesar como string separado por comas
                    productos_tags_raw = request.form.get("productos_tags", "").strip()
                    if productos_tags_raw:
                        productos_tags_list = [tag.lower().strip() for tag in productos_tags_raw.split(",") if tag.strip()]
                        n.productos_tags = json.dumps(productos_tags_list) if productos_tags_list else None
                    else:
                        n.productos_tags = None
            else:
                # Procesar desde input de texto
                productos_tags_raw = request.form.get("productos_tags", "").strip()
                if productos_tags_raw:
                    productos_tags_list = [tag.lower().strip() for tag in productos_tags_raw.split(",") if tag.strip()]
                    n.productos_tags = json.dumps(productos_tags_list) if productos_tags_list else None
                else:
                    n.productos_tags = None

        n.latitud = safe_float(request.form.get("latitud"))
        n.longitud = safe_float(request.form.get("longitud"))

        img = request.files.get("foto")
        if img and img.filename:
            n.imagen_url = save_upload("foto")

        db.session.commit()
        flash("Negocio actualizado exitosamente.")
        return redirect("/admin/comercios")

    return render_template(
        "editar_negocio.html", 
        n=n,
        get_horario_dict=get_horario_dict
    )

@app.route("/admin/noticias")
def gestionar_noticias():
    """Gestionar noticias (listar, crear, editar, eliminar)"""
    if not admin_logged_in():
        return redirect("/login")
    
    ahora = datetime.utcnow()
    noticias_list = Noticia.query.order_by(Noticia.fecha.desc()).all()
    # Agregar información sobre si están caducadas
    for noticia in noticias_list:
        noticia.es_caducada = False
        if noticia.fecha_caducidad and noticia.fecha_caducidad <= ahora:
            noticia.es_caducada = True
    
    return render_template("admin_noticias.html", noticias=noticias_list, ahora=ahora)

@app.route("/admin/noticias/nueva", methods=["GET", "POST"])
def crear_noticia():
    """Crear una nueva noticia"""
    if not admin_logged_in():
        return redirect("/login")
    
    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        contenido = (request.form.get("contenido") or "").strip()
        fecha_caducidad_str = request.form.get("fecha_caducidad", "").strip()
        
        if not titulo or not contenido:
            flash("Título y contenido son obligatorios.")
            return redirect("/admin/noticias/nueva")
        
        imagen_url = save_upload("imagen")
        
        # Procesar fecha de caducidad (opcional)
        fecha_caducidad = None
        if fecha_caducidad_str:
            try:
                # Convertir de formato HTML datetime-local a datetime
                fecha_caducidad = datetime.strptime(fecha_caducidad_str, "%Y-%m-%dT%H:%M")
                # Convertir a UTC si es necesario
            except ValueError:
                flash("Fecha de caducidad inválida. La noticia se creará sin fecha de desaparición.")
        
        nueva_noticia = Noticia(
            titulo=titulo,
            contenido=contenido,
            imagen_url=imagen_url if imagen_url != "/static/uploads/logo.png" else None,
            fecha_caducidad=fecha_caducidad
        )
        
        db.session.add(nueva_noticia)
        db.session.commit()
        
        flash("¡Noticia publicada exitosamente!")
        return redirect("/admin/noticias")
    
    return render_template("crear_noticia.html")

@app.route("/admin/noticias/<int:id>/editar", methods=["GET", "POST"])
def editar_noticia(id):
    """Editar una noticia existente"""
    if not admin_logged_in():
        return redirect("/login")
    
    noticia = db.session.get(Noticia, id)
    if not noticia:
        return "Noticia no encontrada", 404
    
    if request.method == "POST":
        noticia.titulo = (request.form.get("titulo") or "").strip()
        noticia.contenido = (request.form.get("contenido") or "").strip()
        fecha_caducidad_str = request.form.get("fecha_caducidad", "").strip()
        
        img = request.files.get("imagen")
        if img and img.filename:
            noticia.imagen_url = save_upload("imagen")
        
        # Procesar fecha de caducidad (opcional)
        if fecha_caducidad_str:
            try:
                # Convertir de formato HTML datetime-local a datetime
                noticia.fecha_caducidad = datetime.strptime(fecha_caducidad_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Fecha de caducidad inválida. Se mantendrá la fecha anterior.")
        else:
            # Si no se proporciona fecha, eliminar la fecha de caducidad (None = permanente)
            noticia.fecha_caducidad = None
        
        db.session.commit()
        flash("Noticia actualizada.")
        return redirect("/admin/noticias")
    
    return render_template("editar_noticia.html", noticia=noticia)

@app.route("/admin/noticias/<int:id>/eliminar")
def eliminar_noticia(id):
    """Eliminar una noticia"""
    if not admin_logged_in():
        return redirect("/login")
    
    noticia = db.session.get(Noticia, id)
    if not noticia:
        return "Noticia no encontrada", 404
    
    db.session.delete(noticia)
    db.session.commit()
    
    flash("Noticia eliminada.")
    return redirect("/admin/noticias")

# =====================================================
# IMPORTACIÓN DESDE OPENSTREETMAP
# =====================================================

def mapear_categoria_osm(categoria_osm):
    """Mapea tipos de OpenStreetMap a categorías de Ubik2CR"""
    mapeo = {
        # Comida y Bebidas
        "restaurant": "Sodas y Rest.",
        "fast_food": "Comida Rápida",
        "cafe": "Cafeterías",
        "bar": "Bares y Licores",
        "ice_cream": "Heladerías",
        "food_court": "Comida Rápida",
        "bakery": "Panaderías",
        
        # Alimentos
        "supermarket": "Super y Pulpes",
        "greengrocer": "Verdurerías",
        "butcher": "Carnicerías",
        "convenience": "Super y Pulpes",
        
        # Salud
        "pharmacy": "Farmacias",
        "hospital": "CCSS",
        "clinic": "Clínicas y Dr.",
        "dentist": "Dentistas",
        "veterinary": "Veterinarias",
        "optometrist": "Ópticas",
        
        # Belleza y Fitness
        "gym": "Gimnasios",
        "beauty_salon": "Belleza y Barbería",
        "hairdresser": "Belleza y Barbería",
        "spa": "Spas y Masajes",
        
        # Ropa y Tecnología
        "clothes": "Ropa y Calzado",
        "shoes": "Ropa y Calzado",
        "electronics": "Tecnología y Cel.",
        "mobile_phone": "Tecnología y Cel.",
        "computer": "Reparaciones Tech",
        
        # Construcción y Automotriz
        "hardware": "Ferreterías",
        "doityourself": "Ferreterías",
        "car_repair": "Mecánica y Llantas",
        "car_wash": "Lavado de Autos",
        "fuel": "Gasolineras",
        "car": "Automotriz",
        
        # Educación
        "school": "Escuelas",
        "university": "Educacion",
        "library": "Bibliotecas",
        "college": "Educacion",
        
        # Turismo
        "hotel": "Hoteles y Hospedaje",
        "hostel": "Hoteles y Hospedaje",
        "attraction": "Turismo",
        "theme_park": "Cines y Entretenimiento",
        "cinema": "Cines y Entretenimiento",
        
        # Finanzas
        "bank": "Bancos",
        "atm": "Bancos",
        
        # Servicios Públicos
        "police": "Policía",
        "fire_station": "Bomberos",
        "townhall": "Municipalidad",
        "place_of_worship": "Iglesia",
        "government": "Instituciones Públicas",
        
        # Servicios Profesionales
        "lawyer": "Abogados",
        "accountant": "Contables",
        "event_venue": "Salones de Eventos",
        "moving_company": "Mudanzas y Transporte",
        "plumber": "Plomería y Electricidad",
        "electrician": "Plomería y Electricidad",
        "gardener": "Jardinería",
        "pet": "Mascotas y Suministros",
    }
    
    # Buscar coincidencia exacta
    if categoria_osm in mapeo:
        return mapeo[categoria_osm]
    
    # Buscar coincidencia parcial (por si viene "amenity=restaurant")
    categoria_lower = categoria_osm.lower()
    for key, value in mapeo.items():
        if key in categoria_lower:
            return value
    
    # Si no hay coincidencia, usar categoría genérica
    return "Otros"

def obtener_bbox_canton(provincia, canton):
    """Obtiene el bounding box (área) aproximada de un cantón en Costa Rica"""
    # Coordenadas aproximadas de algunos cantones principales
    # Formato: [min_lat, min_lng, max_lat, max_lng]
    bboxes = {
        ("San José", "San José"): [9.85, -84.15, 10.0, -83.95],
        ("San José", "Escazú"): [9.88, -84.15, 9.95, -84.05],
        ("Alajuela", "Alajuela"): [10.0, -84.25, 10.05, -84.15],
        ("Alajuela", "Poás"): [10.05, -84.25, 10.15, -84.15],
        ("Cartago", "Cartago"): [9.85, -83.95, 9.95, -83.85],
        ("Heredia", "Heredia"): [9.95, -84.15, 10.05, -84.05],
        ("Guanacaste", "Liberia"): [10.55, -85.65, 10.65, -85.55],
        ("Puntarenas", "Puntarenas"): [9.95, -84.85, 10.05, -84.75],
        ("Limón", "Limón"): [9.95, -83.05, 10.05, -82.95],
    }
    
    key = (provincia, canton)
    if key in bboxes:
        return bboxes[key]
    
    # Si no está en la lista, usar un bbox genérico de Costa Rica
    # Esto es menos preciso pero funcionará
    return [8.0, -86.0, 11.2, -82.5]

def importar_lugares_osm(provincia, canton, tipos_amenity=None):
    """Importa lugares desde OpenStreetMap usando Overpass API"""
    if not tipos_amenity:
        # Tipos comunes de lugares comerciales en OSM
        tipos_amenity = [
            "restaurant", "fast_food", "cafe", "bar", "pharmacy", "bank", 
            "supermarket", "hospital", "clinic", "school", "hotel", "fuel",
            "car_repair", "hardware", "beauty_salon", "gym", "dentist"
        ]
    
    bbox = obtener_bbox_canton(provincia, canton)
    bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
    
    # Construir query Overpass (sintaxis correcta)
    # Buscar lugares con amenity o shop en el área del cantón
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"]({bbox_str});
      node["shop"]({bbox_str});
      way["amenity"]({bbox_str});
      way["shop"]({bbox_str});
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        # Consultar Overpass API
        overpass_url = "https://overpass-api.de/api/interpreter"
        response = requests.post(overpass_url, data=query, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        elementos = data.get("elements", [])
        
        lugares_importados = []
        lugares_duplicados = 0
        
        for elemento in elementos:
            if elemento.get("type") != "node":
                continue
            
            tags = elemento.get("tags", {})
            if not tags:
                continue
            
            # Obtener información básica
            nombre = tags.get("name") or tags.get("name:es") or "Sin nombre"
            if not nombre or nombre == "Sin nombre":
                continue
            
            # Obtener categoría
            amenity = tags.get("amenity", "")
            shop = tags.get("shop", "")
            categoria_osm = amenity or shop
            categoria = mapear_categoria_osm(categoria_osm)
            
            # Obtener ubicación
            lat = elemento.get("lat")
            lon = elemento.get("lon")
            if not lat or not lon:
                continue
            
            # Obtener dirección
            direccion = tags.get("addr:full") or tags.get("addr:street") or ""
            if direccion and tags.get("addr:housenumber"):
                direccion = f"{tags.get('addr:housenumber')} {direccion}"
            
            # Obtener teléfono
            telefono = tags.get("phone") or tags.get("contact:phone") or None
            
            # Verificar si ya existe (por nombre y coordenadas cercanas)
            existe = Negocio.query.filter(
                Negocio.nombre.ilike(f"%{nombre}%"),
                Negocio.latitud.between(lat - 0.001, lat + 0.001),
                Negocio.longitud.between(lon - 0.001, lon + 0.001)
            ).first()
            
            if existe:
                lugares_duplicados += 1
                continue
            
            # Crear nuevo negocio
            nuevo_negocio = Negocio(
                nombre=nombre[:100],  # Limitar a 100 caracteres
                categoria=categoria,
                ubicacion=direccion[:200] if direccion else f"{canton}, {provincia}",
                provincia=provincia,
                canton=canton,
                distrito=None,  # OSM no siempre tiene distrito
                latitud=lat,
                longitud=lon,
                telefono=telefono[:20] if telefono else None,
                descripcion=f"Lugar importado desde OpenStreetMap. {tags.get('description', '')}"[:500],
                estado="pendiente",  # Requiere aprobación manual
                es_vip=False
            )
            
            db.session.add(nuevo_negocio)
            lugares_importados.append(nuevo_negocio)
        
        db.session.commit()
        
        return {
            "importados": len(lugares_importados),
            "duplicados": lugares_duplicados,
            "total_encontrados": len(elementos)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"[OSM IMPORT ERROR] Error al consultar Overpass API: {e}")
        db.session.rollback()
        return {"error": f"Error al consultar OpenStreetMap: {str(e)}"}
    except Exception as e:
        print(f"[OSM IMPORT ERROR] Error inesperado: {e}")
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}

@app.route("/admin/limpiar-bd", methods=["GET", "POST"])
def limpiar_base_datos():
    """Panel para limpiar la base de datos (solo admin)"""
    if not admin_logged_in():
        return redirect("/login")
    
    if request.method == "POST":
        confirmacion = request.form.get("confirmar", "").strip().lower()
        
        if confirmacion != "limpiar":
            flash("Debés escribir 'limpiar' para confirmar.")
            return redirect("/admin/limpiar-bd")
        
        # Importar y ejecutar script de limpieza
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))
            from scripts.limpiar_base_datos import limpiar_base_datos
            
            print(f"[LIMPIEZA] Iniciando proceso de limpieza...")
            print(f"[LIMPIEZA] Confirmación recibida: '{confirmacion}'")
            
            # Ejecutar limpieza dentro del contexto de la app
            resultado = limpiar_base_datos()
            
            if resultado:
                print(f"[LIMPIEZA] ✅ Proceso completado exitosamente")
                flash("✅ Base de datos limpiada exitosamente. Todas las tablas fueron vaciadas. Las credenciales de admin NO se perdieron (están en variables de entorno).")
            else:
                print(f"[LIMPIEZA] ❌ El script retornó False")
                flash("❌ Error al limpiar la base de datos. El script retornó False. Revisá los logs en Render.com para más detalles.")
        except Exception as e:
            import traceback
            error_msg = str(e) + "\n" + traceback.format_exc()
            print(f"[ERROR LIMPIEZA] {error_msg}")
            print(f"[ERROR LIMPIEZA] Tipo de error: {type(e).__name__}")
            flash(f"❌ Error al limpiar: {str(e)}. Revisá los logs en Render.com para ver el traceback completo.")
        
        return redirect("/admin")
    
    # Mostrar información antes de limpiar
    total_usuarios = Usuario.query.count()
    usuarios_lista = Usuario.query.order_by(Usuario.created_at.desc()).all()
    
    total_noticias = Noticia.query.count()
    noticias_lista = Noticia.query.order_by(Noticia.fecha.desc()).all()
    
    # Estadísticas de vehículos (si existe)
    total_vehiculos = 0
    total_agencias = 0
    vehiculos_lista = []
    if VEHICULOS_AVAILABLE:
        if Vehiculo is not None:
            try:
                total_vehiculos = Vehiculo.query.count()
                vehiculos_lista = Vehiculo.query.order_by(Vehiculo.created_at.desc()).limit(10).all()
            except:
                pass
        if Agencia is not None:
            try:
                total_agencias = Agencia.query.count()
            except:
                pass
    
    # Estadísticas de sistema antiguo (para limpiar también)
    total_negocios = 0
    total_ofertas = 0
    total_mensajes = 0
    total_resenas = 0
    try:
        total_negocios = Negocio.query.count()
        total_ofertas = Oferta.query.count()
        total_mensajes = Mensaje.query.count()
        total_resenas = Resena.query.count()
    except:
        pass
    
    return render_template("admin_limpiar_bd.html", 
                         total_vehiculos=total_vehiculos,
                         total_agencias=total_agencias,
                         total_usuarios=total_usuarios,
                         usuarios_lista=usuarios_lista,
                         total_noticias=total_noticias,
                         noticias_lista=noticias_lista,
                         vehiculos_lista=vehiculos_lista,
                         total_negocios=total_negocios,
                         total_ofertas=total_ofertas,
                         total_mensajes=total_mensajes,
                         total_resenas=total_resenas)

# DEPRECATED: Sistema de importar lugares eliminado (ya no es relevante para vehículos)
@app.route("/admin/importar-osm", methods=["GET", "POST"])
def importar_osm():
    """DEPRECATED: Redirigir al panel principal - ya no se importan lugares"""
    if not admin_logged_in():
        return redirect("/login")
    flash("La importación de lugares ya no está disponible. Esta aplicación ahora es para venta de vehículos.")
    return redirect("/admin")

@app.route("/admin/analytics")
def admin_analytics():
    """Panel de analytics y métricas"""
    if not admin_logged_in():
        return redirect("/login")
    
    from sqlalchemy import func
    from datetime import timedelta
    
    ahora = datetime.utcnow()
    hace_30_dias = ahora - timedelta(days=30)
    hace_7_dias = ahora - timedelta(days=7)
    
    # Visitas totales
    total_visitas = Visita.query.count()
    
    # Visitas últimos 30 días
    visitas_30_dias = Visita.query.filter(Visita.created_at >= hace_30_dias).count()
    
    # Visitas últimos 7 días
    visitas_7_dias = Visita.query.filter(Visita.created_at >= hace_7_dias).count()
    
    # Usuarios únicos (por IP hash) últimos 30 días
    usuarios_unicos_30 = db.session.query(func.count(func.distinct(Visita.ip_hash))).filter(
        Visita.created_at >= hace_30_dias
    ).scalar()
    
    # Visitas por día (últimos 30 días)
    visitas_por_dia = db.session.query(
        func.date(Visita.created_at).label('fecha'),
        func.count(Visita.id).label('cantidad')
    ).filter(
        Visita.created_at >= hace_30_dias
    ).group_by(func.date(Visita.created_at)).order_by('fecha').all()
    
    visitas_por_dia_dict = {str(fecha): cantidad for fecha, cantidad in visitas_por_dia}
    
    # Visitas por hora del día (0-23)
    visitas_por_hora = db.session.query(
        func.extract('hour', Visita.created_at).label('hora'),
        func.count(Visita.id).label('cantidad')
    ).filter(
        Visita.created_at >= hace_30_dias
    ).group_by(func.extract('hour', Visita.created_at)).order_by('hora').all()
    
    visitas_por_hora_dict = {int(hora): cantidad for hora, cantidad in visitas_por_hora}
    # Completar horas faltantes con 0
    horas_completas = {hora: visitas_por_hora_dict.get(hora, 0) for hora in range(24)}
    
    # Páginas más visitadas (top 10)
    paginas_mas_visitadas = db.session.query(
        Visita.url,
        func.count(Visita.id).label('cantidad')
    ).filter(
        Visita.created_at >= hace_30_dias
    ).group_by(Visita.url).order_by(func.count(Visita.id).desc()).limit(10).all()
    
    # Visitas hoy
    hoy = ahora.date()
    visitas_hoy = Visita.query.filter(func.date(Visita.created_at) == hoy).count()
    
    # Visitas ayer
    ayer = (ahora - timedelta(days=1)).date()
    visitas_ayer = Visita.query.filter(func.date(Visita.created_at) == ayer).count()
    
    return render_template(
        "admin_analytics.html",
        total_visitas=total_visitas,
        visitas_30_dias=visitas_30_dias,
        visitas_7_dias=visitas_7_dias,
        visitas_hoy=visitas_hoy,
        visitas_ayer=visitas_ayer,
        usuarios_unicos_30=usuarios_unicos_30 or 0,
        visitas_por_dia_dict=visitas_por_dia_dict,
        visitas_por_hora_dict=horas_completas,
        paginas_mas_visitadas=paginas_mas_visitadas
    )


# =====================================================
# PASSWORD RESET ROUTES
# =====================================================
@app.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()

        flash("Si el correo existe, recibirás un enlace para restablecer tu contraseña.")

        user = Usuario.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(email)
            link = f"{get_base_url_from_request()}/reset/{token}"

            text_body = (
                "Hola,\n\n"
                "Recibimos una solicitud para restablecer tu contraseña.\n"
                "Abrí este enlace para crear una nueva:\n"
                f"{link}\n\n"
                "Este enlace expira en 1 hora.\n\n"
                "Si no fuiste vos, ignorá este correo.\n\n"
                "Ubik2CR"
            )

            html_body = f"""
            <div style="font-family:Arial,sans-serif;background:#f5f7fa;padding:24px">
              <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e6e8ee">
                <div style="background:linear-gradient(90deg,#0b4fa3,#38b24d);color:#fff;padding:18px 20px">
                  <div style="font-size:18px;font-weight:800">Ubik2CR</div>
                  <div style="opacity:.9;font-size:13px;margin-top:4px">Restablecer contraseña</div>
                </div>
                <div style="padding:18px 20px;color:#111827">
                  <p style="margin:0 0 10px 0">Hola,</p>
                  <p style="margin:0 0 14px 0;line-height:1.5">
                    Tocá el botón para crear una nueva contraseña.
                  </p>
                  <div style="text-align:center;margin:18px 0">
                    <a href="{link}" style="display:inline-block;background:#0b4fa3;color:#fff;text-decoration:none;padding:12px 16px;border-radius:10px;font-weight:700">
                      Restablecer contraseña
                    </a>
                  </div>
                  <p style="margin:0 0 10px 0;font-size:13px;opacity:.85;line-height:1.5">
                    Este enlace expira en <b>1 hora</b>. Si no fuiste vos, ignorá este correo.
                  </p>
                  <div style="margin-top:14px;font-size:12px;color:#6b7280;word-break:break-all">
                    Si el botón no abre, copiá este enlace:<br>
                    <a href="{link}">{link}</a>
                  </div>
                </div>
              </div>
              <div style="max-width:520px;margin:10px auto 0 auto;font-size:12px;color:#6b7280;text-align:center">
                © {datetime.now().year} Ubik2CR
              </div>
            </div>
            """

            try:
                send_email(email, "Recuperar contraseña - Ubik2CR", text_body, html_body)
                print(f"[RESET] Email enviado a {email}")
            except Exception as e:
                print(f"[RESET][ERROR] {repr(e)}")
                flash("No se pudo enviar el correo (SMTP). Revisá credenciales/puerto en Secrets.")
                if (os.environ.get("SHOW_RESET_LINK") or "0") == "1":
                    flash(f"(DEV) Link de reseteo: {link}")

        return redirect("/owner/login")

    return render_template("recuperar.html")

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = verify_reset_token(token, expiration=3600)
    if not email:
        return "Enlace inválido o expirado", 400

    user = Usuario.query.filter_by(email=email).first()
    if not user:
        return "Usuario no encontrado", 404

    if request.method == "POST":
        new_password = (request.form.get("password") or "").strip()
        new_password2 = (request.form.get("password2") or "").strip()

        if len(new_password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.")
            return redirect(f"/reset/{token}")

        if new_password != new_password2:
            flash("Las contraseñas no coinciden.")
            return redirect(f"/reset/{token}")

        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Contraseña actualizada correctamente. Iniciá sesión.")
        return redirect("/owner/login")

    return render_template("reset_password.html", token=token, email=email)


# =====================================================
# ERROR PAGES (si existen tus templates)
# =====================================================
@app.errorhandler(404)
def not_found(e):
    try:
        return render_template("404.html"), 404
    except Exception:
        return "404", 404

@app.errorhandler(500)
def server_error(e):
    try:
        return render_template("500.html"), 500
    except Exception:
        return "500", 500


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
