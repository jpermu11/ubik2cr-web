import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Usuario, Negocio, Noticia
from sqlalchemy import or_

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Usamos v2 para asegurar la base de datos correcta
DB_NAME = "ubik2cr_v2.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}
app.secret_key = "clave_maestra_ubik2cr" 
app.permanent_session_lifetime = 31536000 

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- INICIALIZADOR ---
def inicializar_sistema():
    with app.app_context():
        db_path = os.path.join(app.root_path, DB_NAME)
        try:
            db.create_all()
            print("✅ Base de datos verificada correctamente.")
        except Exception as e:
            print(f"⚠️ Error base de datos: {e}")

        # Crear admin si falta
        try:
            mi_email = "admin@ubik2cr.com"
            mi_clave = "UjifamKJ252319@"
            admin = Usuario.query.filter_by(email=mi_email).first()
            if not admin:
                nuevo = Usuario(email=mi_email, password=mi_clave, nombre="Jimmy CEO", rol="admin")
                db.session.add(nuevo)
                db.session.commit()
        except Exception:
            pass

# --- RUTAS PÚBLICAS ---
@app.route('/')
def inicio():
    try:
        busqueda = request.args.get('q')
        categoria = request.args.get('cat')
        query = Negocio.query.filter_by(estado='aprobado').order_by(Negocio.es_vip.desc(), Negocio.calificacion.desc())

        if busqueda:
            query = query.filter(or_(Negocio.nombre.ilike(f'%{busqueda}%'), Negocio.descripcion.ilike(f'%{busqueda}%')))
        if categoria and categoria != "Todas":
            query = query.filter(Negocio.categoria == categoria)

        negocios = query.all()
        return render_template('index.html', negocios=negocios, categoria_actual=categoria)
    except Exception as e:
        return f"<h2>Iniciando sistema...</h2><p>Si ves esto, recarga en 30 segundos. ({e})</p>"

@app.route('/mapa')
def ver_mapa():
    try:
        negocios = Negocio.query.filter_by(estado='aprobado').filter(Negocio.latitud != None).all()
        return render_template('mapa.html', negocios=negocios)
    except Exception:
        return redirect(url_for('inicio'))

@app.route('/noticias')
def ver_noticias():
    noticias = Noticia.query.order_by(Noticia.fecha.desc()).all()
    return render_template('noticias.html', noticias=noticias)

@app.route('/negocio/<int:id>')
def ver_negocio(id):
    negocio = db.session.get(Negocio, id)
    if not negocio: return render_template('404.html'), 404
    return render_template('detalle.html', negocio=negocio)

@app.route('/votar/<int:id>/<int:estrellas>')
def votar_negocio(id, estrellas):
    if estrellas < 1 or estrellas > 5: return redirect(url_for('inicio'))
    clave_memoria = f'voto_guardado_{id}'
    if clave_memoria in session:
        flash("⚠️ Ya votaste antes.", "warning")
        return redirect(url_for('ver_negocio', id=id))
    negocio = db.session.get(Negocio, id)
    if negocio:
        total = negocio.total_votos
        promedio = negocio.calificacion
        nuevo_total = total + 1
        nuevo_promedio = ((promedio * total) + estrellas) / nuevo_total
        negocio.total_votos = nuevo_total
        negocio.calificacion = round(nuevo_promedio, 1)
        db.session.commit()
        session[clave_memoria] = True
        flash("✅ Voto registrado", "success")
    return redirect(url_for('ver_negocio', id=id))

@app.route('/publicar', methods=['GET', 'POST'])
def publicar_negocio():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            categoria = request.form['categoria']
            ubicacion = request.form['ubicacion']
            descripcion = request.form['descripcion']
            telefono = request.form.get('telefono', '')
            whatsapp = request.form.get('whatsapp', '') 
            maps_url = request.form.get('maps_url', '')
            lat = request.form.get('latitud')
            lon = request.form.get('longitud')

            imagen_final = "/static/img/default_negocio.png"
            if 'foto' in request.files:
                file = request.files['foto']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    imagen_final = f"/static/uploads/{filename}"

            nuevo = Negocio(
                nombre=nombre, categoria=categoria, ubicacion=ubicacion, maps_url=maps_url,
                latitud=lat if lat else None, longitud=lon if lon else None,
                descripcion=descripcion, telefono=telefono, whatsapp=whatsapp,
                estado='pendiente', imagen_url=imagen_final, calificacion=5.0, total_votos=1 
            )
            db.session.add(nuevo)
            db.session.commit()
            return render_template('exito.html') 
        except Exception as e:
            return f"Error: {e}"
    return render_template('registro.html') 

# --- RUTAS ADMIN (Resumidas para ahorrar espacio, funcionan igual) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip() 
        password = request.form['password'].strip()
        user = Usuario.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id; session['user_rol'] = user.rol
            return redirect(url_for('admin_dashboard'))
        else: error = "Credenciales incorrectas."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('inicio'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    return render_template('dashboard.html', total=Negocio.query.count(), pendientes=Negocio.query.filter_by(estado='pendiente').count(), activos=Negocio.query.filter_by(estado='aprobado').count())

@app.route('/admin/moderacion')
def admin_moderacion():
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    return render_template('moderacion.html', negocios=Negocio.query.filter_by(estado='pendiente').all())

@app.route('/admin/aprobar/<int:id>', methods=['POST'])
def aprobar_negocio(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    n = db.session.get(Negocio, id)
    if n: n.estado = 'aprobado'; db.session.commit()
    return redirect(url_for('admin_moderacion'))

@app.route('/admin/eliminar/<int:id>', methods=['POST'])
def eliminar_negocio(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    n = db.session.get(Negocio, id)
    if n: db.session.delete(n); db.session.commit()
    return redirect(url_for('admin_moderacion'))

@app.route('/admin/comercios')
def admin_comercios():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('comercios.html', negocios=Negocio.query.filter_by(estado='aprobado').all())

@app.route('/admin/vip/<int:id>', methods=['POST'])
def hacer_vip(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    n = db.session.get(Negocio, id)
    if n: n.es_vip = not n.es_vip; db.session.commit()
    return redirect(url_for('admin_comercios'))

@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
def editar_negocio(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    n = db.session.get(Negocio, id)
    if not n: return redirect(url_for('admin_comercios'))
    if request.method == 'POST':
        n.nombre = request.form['nombre']; n.categoria = request.form['categoria']
        n.descripcion = request.form['descripcion']; n.telefono = request.form['telefono']
        n.whatsapp = request.form['whatsapp']; n.ubicacion = request.form['ubicacion']
        n.maps_url = request.form['maps_url']
        lat = request.form.get('latitud'); lon = request.form.get('longitud')
        if lat and lon: n.latitud = float(lat); n.longitud = float(lon)
        if 'foto' in request.files:
            f = request.files['foto']
            if f and allowed_file(f.filename):
                fname = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                n.imagen_url = f"/static/uploads/{fname}"
        db.session.commit()
        return redirect(url_for('admin_comercios'))
    return render_template('editar_negocio.html', n=n)

@app.route('/admin/noticias')
def admin_noticias():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('admin_noticias.html', noticias=Noticia.query.all())

@app.route('/admin/noticias/crear', methods=['POST'])
def crear_noticia():
    if 'user_id' not in session: return redirect(url_for('login'))
    img = ""
    if 'foto' in request.files:
        f = request.files['foto']
        if f and allowed_file(f.filename):
            fn = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            img = f"/static/uploads/{fn}"
    db.session.add(Noticia(titulo=request.form['titulo'], contenido=request.form['contenido'], imagen_url=img, fecha=datetime.now()))
    db.session.commit()
    return redirect(url_for('admin_noticias'))

@app.route('/admin/noticias/borrar/<int:id>', methods=['POST'])
def borrar_noticia(id):
    n = db.session.get(Noticia, id)
    if n: db.session.delete(n); db.session.commit()
    return redirect(url_for('admin_noticias'))

@app.route('/sobre-nosotros')
def sobre_nosotros(): return render_template('sobre_nosotros.html')
@app.route('/contacto')
def contacto(): return render_template('contacto.html')
@app.route('/categorias')
def categorias(): return redirect(url_for('inicio'))
@app.errorhandler(404)
def p404(e): return render_template('404.html'), 404
@app.errorhandler(500)
def p500(e): return render_template('500.html'), 500

# --- ESTO CORRIGE EL ERROR DE RENDER ---
# Forzamos la creación de DB al importar el archivo
try:
    with app.app_context():
        db.create_all()
        print("✅ DB Inicializada en Render")
except:
    pass

if __name__ == '__main__':
    # Aquí es donde fallaba el espacio antes, ya está corregido:
    app.run(host='0.0.0.0', port=5000)