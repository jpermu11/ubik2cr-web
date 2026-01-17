# encoding: utf-8
"""
UBIK2CR - Venta de Vehículos Usados - Costa Rica
Versión simple desde cero
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

from models import db, Usuario, Vehiculo, Agencia

# App
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "cambiar-en-produccion")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///app.db"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

# Helpers
def admin_logged_in():
    return session.get("rol") == "admin"

def logged_in():
    return "user_id" in session

# RUTAS
@app.route("/")
def index():
    return redirect("/vehiculos")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

@app.route("/vehiculos")
def vehiculos():
    try:
        page = int(request.args.get("page", 1))
    except:
        page = 1
    
    PER_PAGE = 24
    
    # Query base: solo aprobados
    query = Vehiculo.query.filter_by(estado="aprobado")
    
    # FILTROS AVANZADOS
    marca = request.args.get("marca", "").strip()
    modelo = request.args.get("modelo", "").strip()
    tipo = request.args.get("tipo", "").strip()
    año_min = request.args.get("año_min", "").strip()
    año_max = request.args.get("año_max", "").strip()
    precio_min = request.args.get("precio_min", "").strip()
    precio_max = request.args.get("precio_max", "").strip()
    km_max = request.args.get("km_max", "").strip()
    provincia = request.args.get("provincia", "").strip()
    transmision = request.args.get("transmision", "").strip()
    combustible = request.args.get("combustible", "").strip()
    
    if marca:
        query = query.filter_by(marca=marca)
    if modelo:
        query = query.filter(Vehiculo.modelo.ilike(f"%{modelo}%"))
    if tipo:
        query = query.filter_by(tipo=tipo)
    if año_min:
        query = query.filter(Vehiculo.año >= int(año_min))
    if año_max:
        query = query.filter(Vehiculo.año <= int(año_max))
    if precio_min:
        query = query.filter(Vehiculo.precio >= float(precio_min))
    if precio_max:
        query = query.filter(Vehiculo.precio <= float(precio_max))
    if km_max:
        query = query.filter(Vehiculo.kilometraje <= int(km_max))
    if provincia:
        query = query.filter_by(provincia=provincia)
    if transmision:
        query = query.filter_by(transmision=transmision)
    if combustible:
        query = query.filter_by(combustible=combustible)
    
    # ORDENAMIENTO
    orden = request.args.get("orden", "recientes")
    if orden == "precio_asc":
        query = query.order_by(Vehiculo.es_vip.desc(), Vehiculo.precio.asc())
    elif orden == "precio_desc":
        query = query.order_by(Vehiculo.es_vip.desc(), Vehiculo.precio.desc())
    elif orden == "año_desc":
        query = query.order_by(Vehiculo.es_vip.desc(), Vehiculo.año.desc())
    elif orden == "km_asc":
        query = query.order_by(Vehiculo.es_vip.desc(), Vehiculo.kilometraje.asc())
    else:  # recientes
        query = query.order_by(Vehiculo.destacado.desc(), Vehiculo.es_vip.desc(), Vehiculo.created_at.desc())
    
    # PAGINACIÓN
    total = query.count()
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    items = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()
    
    # Obtener marcas únicas para dropdown
    marcas = db.session.query(Vehiculo.marca).filter_by(estado="aprobado").distinct().order_by(Vehiculo.marca).all()
    marcas = [m[0] for m in marcas]
    
    return render_template(
        "vehiculos.html", 
        vehiculos=items, 
        total=total, 
        page=page, 
        total_pages=total_pages,
        marcas=marcas,
        marca_actual=marca
    )

@app.route("/vehiculo/<int:id>")
def vehiculo_detalle(id):
    v = Vehiculo.query.get_or_404(id)
    return render_template("vehiculo.html", vehiculo=v)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["email"] = user.email
            session["rol"] = user.rol
            flash("Sesion iniciada")
            return redirect("/admin" if user.rol == "admin" else "/panel")
        
        flash("Credenciales incorrectas")
    
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        nombre = request.form.get("nombre", "").strip()
        
        if not (email and password and nombre):
            flash("Todos los campos son obligatorios")
            return redirect("/registro")
        
        if Usuario.query.filter_by(email=email).first():
            flash("Email ya registrado")
            return redirect("/registro")
        
        nuevo = Usuario(
            email=email,
            password=generate_password_hash(password),
            nombre=nombre,
            rol="vendedor"
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        session["user_id"] = nuevo.id
        session["email"] = nuevo.email
        session["rol"] = nuevo.rol
        
        flash("Cuenta creada!")
        return redirect("/panel")
    
    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/panel")
def panel():
    if not logged_in():
        return redirect("/login")
    
    user_id = session["user_id"]
    vehiculos = Vehiculo.query.filter_by(owner_id=user_id).order_by(Vehiculo.created_at.desc()).all()
    
    return render_template("panel.html", vehiculos=vehiculos)

@app.route("/publicar", methods=["GET", "POST"])
def publicar():
    if not logged_in():
        return redirect("/login")
    
    if request.method == "POST":
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        año = request.form.get("año", "").strip()
        precio = request.form.get("precio", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        telefono = request.form.get("telefono", "").strip()
        
        if not (marca and modelo and año and precio and descripcion):
            flash("Campos obligatorios faltantes")
            return redirect("/publicar")
        
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
        fecha_venc = datetime.utcnow() + timedelta(days=90)
        
        v = Vehiculo(
            owner_id=session["user_id"],
            marca=marca,
            modelo=modelo,
            año=int(año),
            precio=float(precio),
            descripcion=descripcion,
            telefono=telefono,
            imagen_url=imagen_url,
            fecha_vencimiento=fecha_venc
        )
        
        db.session.add(v)
        db.session.commit()
        
        flash("Vehiculo publicado - en revision")
        return redirect("/panel")
    
    return render_template("publicar.html")

@app.route("/admin")
def admin():
    if not admin_logged_in():
        return redirect("/login")
    
    pendientes = Vehiculo.query.filter_by(estado="pendiente").all()
    aprobados = Vehiculo.query.filter_by(estado="aprobado").limit(20).all()
    
    return render_template("admin.html", pendientes=pendientes, aprobados=aprobados)

@app.route("/admin/aprobar/<int:id>", methods=["POST"])
def aprobar(id):
    if not admin_logged_in():
        return redirect("/login")
    
    v = Vehiculo.query.get_or_404(id)
    v.estado = "aprobado"
    db.session.commit()
    flash("Aprobado")
    return redirect("/admin")

@app.route("/admin/rechazar/<int:id>", methods=["POST"])
def rechazar(id):
    if not admin_logged_in():
        return redirect("/login")
    
    db.session.delete(Vehiculo.query.get_or_404(id))
    db.session.commit()
    flash("Rechazado")
    return redirect("/admin")

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return "<h1>404 - No encontrado</h1>", 404

@app.errorhandler(500)
def error(e):
    return "<h1>500 - Error</h1>", 500

# Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*60}")
    print(f"  UBIK2CR - VENTA DE VEHICULOS")
    print(f"{'='*60}")
    print(f"  URL: http://localhost:{port}")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
