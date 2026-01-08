import os
import smtplib
import threading
import json
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

from sqlalchemy import text
from sqlalchemy.pool import QueuePool

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

from models import db, Negocio, Usuario, Noticia, Resena, Oferta, favoritos


# =====================================================
# APP
# =====================================================
app = Flask(__name__)


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
    # Obtener ofertas activas (no expiradas y de negocios aprobados)
    ahora = datetime.utcnow()
    ofertas_activas = Oferta.query.join(Negocio).filter(
        Negocio.estado == "aprobado",
        Oferta.fecha_caducidad >= ahora,
        Oferta.estado == "activa"
    ).order_by(Oferta.fecha_inicio.desc()).limit(10).all()
    
    q = (request.args.get("q") or "").strip()
    cat = (request.args.get("cat") or "Todas").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    if page < 1:
        page = 1

    PER_PAGE = 24

    query = Negocio.query.filter_by(estado="aprobado")

    if q:
        query = query.filter(Negocio.nombre.ilike(f"%{q}%"))
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
        q=q,
        cat=cat,
        ofertas_activas=ofertas_activas,
        owner_logged_in=owner_logged_in(),
        admin_logged_in=admin_logged_in(),
        get_safe_image_url=get_safe_image_url,
    )

@app.route("/cuenta")
def cuenta():
    return render_template("cuenta.html")

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
    noticias_list = Noticia.query.order_by(Noticia.fecha.desc()).all()
    return render_template("noticias.html", noticias=noticias_list)

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
# OWNER AUTH (DUEÑOS)
# =====================================================
@app.route("/owner/registro", methods=["GET", "POST"])
def owner_registro():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        nombre = (request.form.get("nombre") or "").strip()

        if not email or not password:
            flash("Por favor ingresá email y contraseña.")
            return redirect("/owner/registro")

        existe = Usuario.query.filter_by(email=email).first()
        if existe:
            flash("Ese correo ya existe. Iniciá sesión.")
            return redirect("/owner/login")

        pwd_hash = generate_password_hash(password)

        nuevo = Usuario(email=email, password=pwd_hash, nombre=nombre, rol="OWNER")
        db.session.add(nuevo)
        db.session.commit()

        session["user_id"] = nuevo.id
        session["user_email"] = nuevo.email
        session["user_rol"] = nuevo.rol

        flash("Cuenta creada. Ahora podés crear tus negocios.")
        return redirect("/panel")

    return render_template("owner_registro.html")

@app.route("/owner/login", methods=["GET", "POST"])
def owner_login():
    if request.method == "POST":
        email = (request.form.get("usuario") or request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()

        u = Usuario.query.filter_by(email=email).first()
        if not u:
            flash("No existe ese usuario.")
            return redirect("/owner/login")

        if not normalize_password_check(u.password, password):
            flash("Contraseña incorrecta. Si la olvidaste, usá '¿Olvidaste tu contraseña?'.")
            return redirect("/owner/login")

        # Si venía en texto plano en algún momento, se actualiza a hash
        if not (u.password.startswith(("pbkdf2:", "scrypt:"))):
            u.password = generate_password_hash(password)
            db.session.commit()

        session["user_id"] = u.id
        session["user_email"] = u.email
        session["user_rol"] = u.rol

        return redirect("/panel")

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
    if not owner_required():
        return redirect("/cuenta")

    # Si por alguna razón el modelo no tiene owner_id todavía, evitamos crash
    if not hasattr(Negocio, "owner_id"):
        flash("Falta el campo owner_id en Negocio. Necesita migración.")
        return render_template("panel_owner.html", negocios=[])

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
        user_email=session.get("user_email"),
        ahora=ahora,
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
        negocio.descripcion = request.form.get("descripcion", negocio.descripcion)
        negocio.telefono = request.form.get("telefono", negocio.telefono)
        negocio.whatsapp = request.form.get("whatsapp", negocio.whatsapp)
        # Horario
        negocio.abierto_24h = bool(request.form.get("abierto_24h"))
        if negocio.abierto_24h:
            negocio.horario = None  # Si está 24h, no guardar horario específico
        else:
            negocio.horario = parse_horario_from_form(request.form)
        negocio.maps_url = request.form.get("maps_url", negocio.maps_url)

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

        imagen_url = save_upload("foto")

        nuevo_negocio = Negocio(
            nombre=nombre,
            categoria=categoria,
            ubicacion=ubicacion,
            latitud=latitud,
            longitud=longitud,
            maps_url=maps_url,
            telefono=telefono,
            whatsapp=whatsapp,
            horario=horario,
            abierto_24h=abierto_24h,
            descripcion=descripcion,
            imagen_url=imagen_url,
            estado="pendiente",
            es_vip=False,
        )

        # Si existe owner_id en el modelo, lo asignamos
        if hasattr(Negocio, "owner_id"):
            setattr(nuevo_negocio, "owner_id", session["user_id"])

        db.session.add(nuevo_negocio)
        db.session.commit()
        return render_template("exito.html")

    return render_template("registro.html")


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

    total_pendientes = Negocio.query.filter_by(estado="pendiente").count()
    total_activos = Negocio.query.filter_by(estado="aprobado").count()
    total_vip = Negocio.query.filter_by(estado="aprobado", es_vip=True).count()

    # 👇 Compatibilidad con tu dashboard viejo: p/a/v
    return render_template("dashboard.html", p=total_pendientes, a=total_activos, v=total_vip)

@app.route("/admin/comercios")
def gestionar_comercios():
    if not admin_logged_in():
        return redirect("/login")

    pendientes = Negocio.query.filter_by(estado="pendiente").order_by(Negocio.id.desc()).all()
    activos = Negocio.query.filter_by(estado="aprobado").order_by(Negocio.es_vip.desc(), Negocio.id.desc()).all()

    return render_template("comercios.html", pendientes=pendientes, activos=activos)

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
        n.descripcion = request.form.get("descripcion", n.descripcion)
        n.telefono = request.form.get("telefono", n.telefono)
        n.whatsapp = request.form.get("whatsapp", n.whatsapp)
        # Horario
        n.abierto_24h = bool(request.form.get("abierto_24h"))
        if n.abierto_24h:
            n.horario = None  # Si está 24h, no guardar horario específico
        else:
            n.horario = parse_horario_from_form(request.form)
        n.maps_url = request.form.get("maps_url", n.maps_url)

        n.latitud = safe_float(request.form.get("latitud"))
        n.longitud = safe_float(request.form.get("longitud"))

        img = request.files.get("foto")
        if img and img.filename:
            n.imagen_url = save_upload("foto")

        db.session.commit()
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
    
    noticias_list = Noticia.query.order_by(Noticia.fecha.desc()).all()
    return render_template("admin_noticias.html", noticias=noticias_list)

@app.route("/admin/noticias/nueva", methods=["GET", "POST"])
def crear_noticia():
    """Crear una nueva noticia"""
    if not admin_logged_in():
        return redirect("/login")
    
    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        contenido = (request.form.get("contenido") or "").strip()
        
        if not titulo or not contenido:
            flash("Título y contenido son obligatorios.")
            return redirect("/admin/noticias/nueva")
        
        imagen_url = save_upload("imagen")
        
        nueva_noticia = Noticia(
            titulo=titulo,
            contenido=contenido,
            imagen_url=imagen_url if imagen_url != "/static/uploads/logo.png" else None
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
        
        img = request.files.get("imagen")
        if img and img.filename:
            noticia.imagen_url = save_upload("imagen")
        
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
