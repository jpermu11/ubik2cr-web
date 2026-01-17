"""
UBIK2CR - PLATAFORMA DE VENTA DE VEHÍCULOS USADOS
Sistema para Costa Rica - Vendedores individuales y agencias
"""
import os
import smtplib
import json
from email.message import EmailMessage
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session, flash
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from sqlalchemy import text, or_, func
from sqlalchemy import inspect as sqlalchemy_inspect

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

from models import db, Usuario, Vehiculo, Agencia, ImagenVehiculo, Resena, favoritos_vehiculos, Visita

# =====================================================
# APP
# =====================================================
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_cambiar")

# =====================================================
# DATABASE
# =====================================================
DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()

if not DATABASE_URL:
    # Desarrollo local: usar SQLite
    DATABASE_URL = "sqlite:///app.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
else:
    # Producción: PostgreSQL
    if "sslmode=" not in DATABASE_URL:
        DATABASE_URL += ("&" if "?" in DATABASE_URL else "?") + "sslmode=prefer"
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# =====================================================
# CLOUDINARY
# =====================================================
if CLOUDINARY_AVAILABLE:
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
    api_key = os.environ.get("CLOUDINARY_API_KEY", "").strip()
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
    
    if cloud_name and api_key and api_secret:
        cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
        USE_CLOUDINARY = True
    else:
        USE_CLOUDINARY = False
else:
    USE_CLOUDINARY = False

# =====================================================
# UPLOADS
# =====================================================
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# =====================================================
# INIT DB
# =====================================================
db.init_app(app)
migrate = Migrate(app, db)

# =====================================================
# HELPERS
# =====================================================
def admin_logged_in():
    return session.get("rol") == "admin"

def owner_logged_in():
    return "user_id" in session

def get_safe_image_url(imagen_url):
    if not imagen_url:
        return "https://via.placeholder.com/600x400?text=Ubik2CR"
    if imagen_url.startswith("http"):
        return imagen_url
    return imagen_url

# =====================================================
# EMAIL
# =====================================================
def send_email(to_email, subject, text_body, html_body=None):
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASS", "").strip()
    
    if not (smtp_host and smtp_user and smtp_pass):
        print("[EMAIL] SMTP no configurado")
        return
    
    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_body)
    
    if html_body:
        msg.add_alternative(html_body, subtype="html")
    
    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        print(f"[EMAIL] Enviado a {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

# =====================================================
# ANALYTICS
# =====================================================
@app.before_request
def registrar_visita():
    try:
        if not hasattr(request, 'path'):
            return None
            
        path = request.path
        
        # Excluir rutas de admin y estáticas
        if path.startswith('/admin') or path.startswith('/static') or path.startswith('/health'):
            return None
        
        import hashlib
        ip = request.remote_addr or "unknown"
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
        
        user_agent = request.headers.get('User-Agent', '')[:200]
        referrer = request.headers.get('Referer', '')[:500]
        
        try:
            visita = Visita(
                ip_hash=ip_hash,
                url=path,
                user_agent=user_agent,
                referrer=referrer
            )
            db.session.add(visita)
            db.session.commit()
        except:
            db.session.rollback()
    except:
        pass
    
    return None

# =====================================================
# RUTAS PRINCIPALES
# =====================================================
@app.route("/")
def index():
    """Página principal - redirige a búsqueda de vehículos"""
    return redirect("/vehiculos")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

@app.route("/health/db")
def health_db():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

# =====================================================
# BÚSQUEDA DE VEHÍCULOS
# =====================================================
@app.route("/vehiculos")
def buscar_vehiculos():
    """Página principal de búsqueda de vehículos"""
    try:
        page = int(request.args.get("page", 1))
    except:
        page = 1
    
    PER_PAGE = 24
    
    # Query: solo vehículos aprobados
    query = Vehiculo.query.filter_by(estado="aprobado")
    
    # Filtros
    marca = request.args.get("marca", "").strip()
    if marca:
        query = query.filter_by(marca=marca)
    
    # Ordenar
    query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.created_at.desc())
    
    # Paginación
    total = query.count()
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    vehiculos = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()
    
    # Obtener marcas únicas
    marcas = db.session.query(Vehiculo.marca).filter_by(estado="aprobado").distinct().order_by(Vehiculo.marca).all()
    marcas = [m[0] for m in marcas]
    
    return render_template(
        "vehiculos_index.html",
        vehiculos=vehiculos,
        total=total,
        page=page,
        total_pages=total_pages,
        marcas=marcas,
        marca_actual=marca
    )

@app.route("/vehiculo/<int:id>")
def detalle_vehiculo(id):
    """Detalle de un vehículo"""
    vehiculo = Vehiculo.query.get_or_404(id)
    
    # Solo mostrar si está aprobado (o si es el dueño/admin)
    if vehiculo.estado != "aprobado":
        if not owner_logged_in() or (session.get("user_id") != vehiculo.owner_id and not admin_logged_in()):
            flash("Este vehículo no está disponible.")
            return redirect("/vehiculos")
    
    # Obtener imágenes adicionales
    imagenes = ImagenVehiculo.query.filter_by(vehiculo_id=id).order_by(ImagenVehiculo.orden).all()
    
    return render_template("vehiculo_detalle.html", vehiculo=vehiculo, imagenes_adicionales=imagenes)

# =====================================================
# AUTENTICACIÓN
# =====================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Login para admin"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if user.rol == "admin":
                session["user_id"] = user.id
                session["user_email"] = user.email
                session["rol"] = user.rol
                flash("Sesión iniciada correctamente.")
                return redirect("/admin")
        
        flash("Credenciales incorrectas.")
    
    return render_template("login.html")

@app.route("/owner/registro", methods=["GET", "POST"])
def owner_registro():
    """Registro de vendedores"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        
        if not (email and password and nombre):
            flash("Todos los campos son obligatorios.")
            return redirect("/owner/registro")
        
        # Verificar si el email ya existe
        existente = Usuario.query.filter_by(email=email).first()
        if existente:
            flash("Este email ya está registrado.")
            return redirect("/owner/registro")
        
        # Crear usuario
        nuevo = Usuario(
            email=email,
            password=generate_password_hash(password),
            nombre=nombre,
            telefono=telefono,
            rol="vendedor",
            tipo_usuario="individual"
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        # Iniciar sesión automáticamente
        session["user_id"] = nuevo.id
        session["user_email"] = nuevo.email
        session["rol"] = nuevo.rol
        
        flash("Cuenta creada exitosamente!")
        return redirect("/panel")
    
    return render_template("owner_registro.html")

@app.route("/owner/login", methods=["GET", "POST"])
def owner_login():
    """Login para vendedores"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_email"] = user.email
            session["rol"] = user.rol
            flash("Sesión iniciada correctamente.")
            return redirect("/panel")
        
        flash("Credenciales incorrectas.")
    
    return render_template("owner_login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect("/")

# =====================================================
# PANEL VENDEDOR
# =====================================================
@app.route("/panel")
def panel():
    """Panel del vendedor"""
    if not owner_logged_in():
        flash("Debes iniciar sesión primero.")
        return redirect("/owner/login")
    
    user_id = session["user_id"]
    
    # Obtener vehículos del vendedor
    vehiculos = Vehiculo.query.filter_by(owner_id=user_id).order_by(Vehiculo.created_at.desc()).all()
    
    # Estadísticas
    total = len(vehiculos)
    aprobados = len([v for v in vehiculos if v.estado == "aprobado"])
    pendientes = len([v for v in vehiculos if v.estado == "pendiente"])
    vendidos = len([v for v in vehiculos if v.estado == "vendido"])
    
    return render_template(
        "panel_vehiculos.html",
        vehiculos=vehiculos,
        total=total,
        aprobados=aprobados,
        pendientes=pendientes,
        vendidos=vendidos,
        user_email=session["user_email"],
        datetime=datetime
    )

@app.route("/vehiculos/publicar", methods=["GET", "POST"])
def publicar_vehiculo():
    """Publicar un nuevo vehículo"""
    if not owner_logged_in():
        flash("Debes iniciar sesión primero.")
        return redirect("/owner/login")
    
    if request.method == "POST":
        # Obtener datos del formulario
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        año = request.form.get("año", "").strip()
        precio = request.form.get("precio", "").strip()
        kilometraje = request.form.get("kilometraje", "").strip()
        tipo_vehiculo = request.form.get("tipo_vehiculo", "").strip()
        transmision = request.form.get("transmision", "").strip()
        combustible = request.form.get("combustible", "").strip()
        color = request.form.get("color", "").strip()
        estado_vehiculo = request.form.get("estado_vehiculo", "usado").strip()
        descripcion = request.form.get("descripcion", "").strip()
        provincia = request.form.get("provincia", "").strip()
        telefono = request.form.get("telefono", "").strip()
        whatsapp = request.form.get("whatsapp", "").strip()
        
        # Validaciones
        if not (marca and modelo and año and precio and descripcion):
            flash("Los campos marca, modelo, año, precio y descripción son obligatorios.")
            return redirect("/vehiculos/publicar")
        
        try:
            año_int = int(año)
            precio_float = float(precio)
            km_int = int(kilometraje) if kilometraje else 0
        except:
            flash("Los valores numéricos no son válidos.")
            return redirect("/vehiculos/publicar")
        
        # Subir imagen
        imagen_url = None
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen and imagen.filename:
                filename = secure_filename(imagen.filename)
                path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                imagen.save(path)
                imagen_url = f"/static/uploads/{filename}"
        
        # Crear vehículo
        fecha_vencimiento = datetime.utcnow() + timedelta(days=90)  # 3 meses
        
        nuevo_vehiculo = Vehiculo(
            owner_id=session["user_id"],
            marca=marca,
            modelo=modelo,
            año=año_int,
            precio=precio_float,
            kilometraje=km_int,
            tipo_vehiculo=tipo_vehiculo,
            transmision=transmision,
            combustible=combustible,
            color=color,
            estado_vehiculo=estado_vehiculo,
            descripcion=descripcion,
            provincia=provincia,
            telefono=telefono,
            whatsapp=whatsapp,
            imagen_url=imagen_url,
            estado="pendiente",
            fecha_vencimiento=fecha_vencimiento,
            notificacion_vencimiento_enviada=False
        )
        
        db.session.add(nuevo_vehiculo)
        db.session.commit()
        
        flash("Vehículo publicado! Será revisado por un administrador.")
        return redirect("/panel")
    
    # Cargar ubicaciones de Costa Rica
    ubicaciones_data = {}
    try:
        json_path = os.path.join(os.path.dirname(__file__), "static", "data", "costa_rica_ubicaciones.json")
        with open(json_path, "r", encoding="utf-8") as f:
            ubicaciones_data = json.load(f)
    except:
        pass
    
    return render_template("publicar_vehiculo.html", ubicaciones_data=ubicaciones_data)

# =====================================================
# PANEL ADMIN
# =====================================================
@app.route("/admin")
def admin():
    """Panel de administración"""
    if not admin_logged_in():
        flash("Acceso denegado.")
        return redirect("/login")
    
    total_usuarios = Usuario.query.count()
    total_vehiculos = Vehiculo.query.count()
    vehiculos_pendientes = Vehiculo.query.filter_by(estado="pendiente").count()
    vehiculos_aprobados = Vehiculo.query.filter_by(estado="aprobado").count()
    
    return render_template(
        "admin.html",
        total_usuarios=total_usuarios,
        total_vehiculos=total_vehiculos,
        vehiculos_pendientes=vehiculos_pendientes,
        vehiculos_aprobados=vehiculos_aprobados
    )

@app.route("/admin/vehiculos")
def admin_vehiculos():
    """Gestión de vehículos"""
    if not admin_logged_in():
        return redirect("/login")
    
    pendientes = Vehiculo.query.filter_by(estado="pendiente").order_by(Vehiculo.created_at.desc()).all()
    aprobados = Vehiculo.query.filter_by(estado="aprobado").order_by(Vehiculo.created_at.desc()).limit(50).all()
    
    return render_template("admin_vehiculos.html", pendientes=pendientes, aprobados=aprobados, datetime=datetime)

@app.route("/admin/vehiculo/<int:id>/aprobar", methods=["POST"])
def aprobar_vehiculo(id):
    """Aprobar vehículo"""
    if not admin_logged_in():
        return redirect("/login")
    
    vehiculo = Vehiculo.query.get_or_404(id)
    vehiculo.estado = "aprobado"
    db.session.commit()
    
    flash(f"Vehículo {vehiculo.marca} {vehiculo.modelo} aprobado.")
    return redirect("/admin/vehiculos")

@app.route("/admin/vehiculo/<int:id>/rechazar", methods=["POST"])
def rechazar_vehiculo(id):
    """Rechazar vehículo"""
    if not admin_logged_in():
        return redirect("/login")
    
    vehiculo = Vehiculo.query.get_or_404(id)
    vehiculo.estado = "eliminado"
    db.session.commit()
    
    flash(f"Vehículo {vehiculo.marca} {vehiculo.modelo} rechazado.")
    return redirect("/admin/vehiculos")

# =====================================================
# ERROR HANDLERS
# =====================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html") if os.path.exists("templates/404.html") else ("404 - Página no encontrada", 404)

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html") if os.path.exists("templates/500.html") else ("500 - Error del servidor", 500)

# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*60}")
    print(f"  UBIK2CR - VENTA DE VEHICULOS USADOS")
    print(f"{'='*60}")
    print(f"\n  URL: http://localhost:{port}\n")
    print(f"  Presiona Ctrl+C para detener")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
