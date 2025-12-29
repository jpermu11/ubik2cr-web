import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Usuario, Negocio, Noticia
from sqlalchemy import or_

app = Flask(__name__)

# --- CONFIGURACIÓN ---
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

# --- INICIALIZADOR (VERSIÓN "NUCLEAR") ---
def inicializar_sistema():
    with app.app_context():
        # 1. Definimos la ruta de la base de datos
        db_path = os.path.join(app.root_path, DB_NAME)

        # 2. INTENTO DE REPARACIÓN INTELIGENTE
        # Si la base de datos existe, intentamos leerla. Si falla, la borramos.
        if os.path.exists(db_path):
            try:
                # Prueba: Intentar leer la columna nueva 'latitud'
                db.session.execute(db.text("SELECT latitud FROM negocios LIMIT 1"))
                print("✅ Base de datos verificada correctamente.")
            except Exception:
                print("⚠️ ESTRUCTURA ANTIGUA DETECTADA. REINICIANDO BASE DE DATOS...")
                db.session.remove() # Cerramos conexión
                db.drop_all()       # Borramos tablas internas
                os.remove(db_path)  # Borramos el archivo físico

        # 3. Creamos todo desde cero (ahora sí con la estructura nueva)
        db.create_all()

        # 4. Creamos al Admin por defecto
        mi_email = "admin@ubik2cr.com"
        mi_clave = "UjifamKJ252319@"
        admin = Usuario.query.filter_by(email=mi_email).first()
        if not admin:
            nuevo = Usuario(email=mi_email, password=mi_clave, nombre="Jimmy CEO", rol="admin")
            db.session.add(nuevo)
            db.session.commit()
            print("👤 Usuario Admin Creado.")

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
        # Si falla aquí, mostramos el error claro en vez de 500
        return f"<h2>Error cargando la página:</h2><p>{e}</p><p>Intenta darle Stop y Run de nuevo.</p>"

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
        flash("⚠️ Ya votaste por este negocio anteriormente.", "warning")
        return redirect(url_for('ver_negocio', id=id))
    negocio = db.session.get(Negocio, id)
    if negocio:
        total_actual = negocio.total_votos
        promedio_actual = negocio.calificacion
        nuevo_total = total_actual + 1
        nuevo_promedio = ((promedio_actual * total_actual) + estrellas) / nuevo_total
        negocio.total_votos = nuevo_total
        negocio.calificacion = round(nuevo_promedio, 1)
        db.session.commit()
        session[clave_memoria] = True
        session.permanent = True
        flash("✅ ¡Voto registrado exitosamente!", "success")
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

            latitud = request.form.get('latitud')
            longitud = request.form.get('longitud')

            imagen_final = "/static/img/default_negocio.png"
            if 'foto' in request.files:
                file = request.files['foto']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    imagen_final = f"/static/uploads/{filename}"

            nuevo_negocio = Negocio(
                nombre=nombre, categoria=categoria, ubicacion=ubicacion, maps_url=maps_url,
                latitud=latitud if latitud else None, longitud=longitud if longitud else None,
                descripcion=descripcion, telefono=telefono, whatsapp=whatsapp,
                estado='pendiente', imagen_url=imagen_final,
                calificacion=5.0, total_votos=1 
            )
            db.session.add(nuevo_negocio)
            db.session.commit()
            return render_template('exito.html') 
        except Exception as e:
            return f"Error: {e}"
    return render_template('registro.html') 

# --- RUTAS ADMIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip() 
        password = request.form['password'].strip()
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.password == password:
            session['user_id'] = usuario.id
            session['user_rol'] = usuario.rol
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Credenciales incorrectas."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('inicio'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    total = Negocio.query.count()
    pendientes = Negocio.query.filter_by(estado='pendiente').count()
    activos = Negocio.query.filter_by(estado='aprobado').count()
    return render_template('dashboard.html', total=total, pendientes=pendientes, activos=activos)

@app.route('/admin/moderacion')
def admin_moderacion():
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    pendientes = Negocio.query.filter_by(estado='pendiente').all()
    return render_template('moderacion.html', negocios=pendientes)

@app.route('/admin/aprobar/<int:id>', methods=['POST'])
def aprobar_negocio(id):
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    n = db.session.get(Negocio, id)
    if n: n.estado = 'aprobado'; db.session.commit(); flash("✅ Negocio Aprobado", "success")
    return redirect(url_for('admin_moderacion'))

@app.route('/admin/eliminar/<int:id>', methods=['POST'])
def eliminar_negocio(id):
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    n = db.session.get(Negocio, id)
    origen = request.args.get('origen', 'moderacion')
    if n: db.session.delete(n); db.session.commit(); flash("🗑️ Negocio Eliminado", "warning")
    if origen == 'activos': return redirect(url_for('admin_comercios'))
    return redirect(url_for('admin_moderacion'))

@app.route('/admin/comercios')
def admin_comercios():
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    negocios = Negocio.query.filter_by(estado='aprobado').order_by(Negocio.es_vip.desc(), Negocio.id.desc()).all()
    return render_template('comercios.html', negocios=negocios)

@app.route('/admin/vip/<int:id>', methods=['POST'])
def hacer_vip(id):
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    n = db.session.get(Negocio, id)
    if n:
        n.es_vip = not n.es_vip
        db.session.commit()
        estado = "VIP 👑" if n.es_vip else "Normal"
        flash(f"Negocio actualizado a: {estado}", "success")
    return redirect(url_for('admin_comercios'))

@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
def editar_negocio(id):
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    negocio = db.session.get(Negocio, id)
    if not negocio: return redirect(url_for('admin_comercios'))
    if request.method == 'POST':
        negocio.nombre = request.form['nombre']
        negocio.categoria = request.form['categoria']
        negocio.descripcion = request.form['descripcion']
        negocio.telefono = request.form['telefono']
        negocio.whatsapp = request.form['whatsapp']
        negocio.ubicacion = request.form['ubicacion']
        negocio.maps_url = request.form['maps_url']

        lat = request.form.get('latitud')
        lon = request.form.get('longitud')
        if lat and lon:
            negocio.latitud = float(lat)
            negocio.longitud = float(lon)

        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                negocio.imagen_url = f"/static/uploads/{filename}"
        db.session.commit()
        flash("💾 Cambios guardados correctamente", "success")
        return redirect(url_for('admin_comercios'))
    return render_template('editar_negocio.html', n=negocio)

@app.route('/admin/noticias')
def admin_noticias():
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    noticias = Noticia.query.order_by(Noticia.fecha.desc()).all()
    return render_template('admin_noticias.html', noticias=noticias)

@app.route('/admin/noticias/crear', methods=['POST'])
def crear_noticia():
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
    titulo = request.form['titulo']
    contenido = request.form['contenido']
    imagen_url = ""
    if 'foto' in request.files:
        file = request.files['foto']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_url = f"/static/uploads/{filename}"
    nueva = Noticia(titulo=titulo, contenido=contenido, imagen_url=imagen_url, fecha=datetime.now())
    db.session.add(nueva)
    db.session.commit()
    return redirect(url_for('admin_noticias'))

@app.route('/admin/noticias/borrar/<int:id>', methods=['POST'])
def borrar_noticia(id):
    if 'user_id' not in session or session.get('user_rol') != 'admin': return redirect(url_for('login'))
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
def pagina_no_encontrada(e): return render_template('404.html'), 404
@app.errorhandler(500)
def error_servidor(e): return render_template('500.html'), 500

if __name__ == '__main__':
 if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)