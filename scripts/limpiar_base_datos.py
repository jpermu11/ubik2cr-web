"""
Script de Limpieza de Base de Datos
Limpia todos los datos excepto la estructura de tablas
Mantiene las credenciales de admin (están en variables de entorno)
"""
from models import db, Negocio, Usuario, Noticia, Resena, Oferta, Mensaje, ImagenNegocio, Visita
from sqlalchemy import text, inspect

def limpiar_base_datos():
    """Limpia todos los datos de las tablas (incluye sistema antiguo y nuevo si existe)"""
    print("🧹 Iniciando limpieza de base de datos...")
    
    try:
        # Verificar qué tablas existen en la BD
        inspector = inspect(db.engine)
        tablas_existentes = inspector.get_table_names()
        print(f"📋 Tablas encontradas en BD: {', '.join(tablas_existentes)}")
        
        # Limpiar tablas del sistema de vehículos (si existen)
        if 'imagenes_vehiculos' in tablas_existentes:
            print("  - Eliminando imágenes de vehículos...")
            try:
                db.session.execute(text("DELETE FROM imagenes_vehiculos"))
                print(f"    ✅ Imágenes de vehículos eliminadas")
            except Exception as e:
                print(f"    ⚠️ Error eliminando imágenes de vehículos: {e}")
        
        if 'favoritos_vehiculos' in tablas_existentes:
            print("  - Eliminando favoritos de vehículos...")
            try:
                db.session.execute(text("DELETE FROM favoritos_vehiculos"))
                print(f"    ✅ Favoritos de vehículos eliminados")
            except Exception as e:
                print(f"    ⚠️ Error eliminando favoritos de vehículos: {e}")
        
        if 'vehiculos' in tablas_existentes:
            print("  - Eliminando vehículos...")
            try:
                db.session.execute(text("DELETE FROM vehiculos"))
                print(f"    ✅ Vehículos eliminados")
            except Exception as e:
                print(f"    ⚠️ Error eliminando vehículos: {e}")
        
        if 'agencias' in tablas_existentes:
            print("  - Eliminando agencias...")
            try:
                db.session.execute(text("DELETE FROM agencias"))
                print(f"    ✅ Agencias eliminadas")
            except Exception as e:
                print(f"    ⚠️ Error eliminando agencias: {e}")
        
        # Limpiar tablas del sistema antiguo (negocios)
        if 'imagenes_negocios' in tablas_existentes:
            print("  - Eliminando imágenes de negocios...")
            try:
                ImagenNegocio.query.delete()
                print(f"    ✅ Imágenes de negocios eliminadas")
            except Exception as e:
                print(f"    ⚠️ Error eliminando imágenes de negocios: {e}")
        
        if 'favoritos' in tablas_existentes:
            print("  - Eliminando favoritos...")
            try:
                db.session.execute(text("DELETE FROM favoritos"))
                print(f"    ✅ Favoritos eliminados")
            except Exception as e:
                print(f"    ⚠️ Error eliminando favoritos: {e}")
        
        if 'resenas' in tablas_existentes:
            print("  - Eliminando reseñas...")
            try:
                Resena.query.delete()
                print(f"    ✅ Reseñas eliminadas")
            except Exception as e:
                print(f"    ⚠️ Error eliminando reseñas: {e}")
        
        if 'mensajes' in tablas_existentes:
            print("  - Eliminando mensajes...")
            try:
                Mensaje.query.delete()
                print(f"    ✅ Mensajes eliminados")
            except Exception as e:
                print(f"    ⚠️ Error eliminando mensajes: {e}")
        
        if 'ofertas' in tablas_existentes:
            print("  - Eliminando ofertas...")
            try:
                Oferta.query.delete()
                print(f"    ✅ Ofertas eliminadas")
            except Exception as e:
                print(f"    ⚠️ Error eliminando ofertas: {e}")
        
        if 'noticias' in tablas_existentes:
            print("  - Eliminando noticias...")
            try:
                Noticia.query.delete()
                print(f"    ✅ Noticias eliminadas")
            except Exception as e:
                print(f"    ⚠️ Error eliminando noticias: {e}")
        
        if 'negocios' in tablas_existentes:
            print("  - Eliminando negocios...")
            try:
                Negocio.query.delete()
                print(f"    ✅ Negocios eliminados")
            except Exception as e:
                print(f"    ⚠️ Error eliminando negocios: {e}")
        
        # Limpiar usuarios (ADMIN está en variables de entorno, no en BD)
        if 'usuarios' in tablas_existentes:
            print("  - Eliminando usuarios...")
            try:
                total_usuarios = Usuario.query.count()
                Usuario.query.delete()
                print(f"    ✅ {total_usuarios} usuarios eliminados")
                print(f"    📝 Nota: Las credenciales de admin NO se perdieron (están en variables de entorno)")
            except Exception as e:
                print(f"    ⚠️ Error eliminando usuarios: {e}")
        
        # Opcional: Limpiar visitas (comentado por defecto para mantener analytics)
        if 'visitas' in tablas_existentes:
            print("  - Visitas: Manteniendo para analytics (comentar línea en script para limpiar)")
            # Descomentar para limpiar también visitas:
            # Visita.query.delete()
        
        # HACER COMMIT de todos los cambios
        print("\n💾 Guardando cambios en la base de datos...")
        db.session.commit()
        print("✅ Commit realizado exitosamente")
        
        # Verificar que las tablas estén vacías
        print("\n🔍 Verificando limpieza...")
        if 'negocios' in tablas_existentes:
            count_negocios = db.session.execute(text("SELECT COUNT(*) FROM negocios")).scalar()
            print(f"  - Negocios restantes: {count_negocios}")
        if 'usuarios' in tablas_existentes:
            count_usuarios = db.session.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
            print(f"  - Usuarios restantes: {count_usuarios}")
        if 'vehiculos' in tablas_existentes:
            count_vehiculos = db.session.execute(text("SELECT COUNT(*) FROM vehiculos")).scalar()
            print(f"  - Vehículos restantes: {count_vehiculos}")
        
        print("\n✅ Limpieza completada exitosamente!")
        print("📝 Nota: Las credenciales de admin NO se perdieron (están en variables de entorno)")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error durante la limpieza: {e}")
        import traceback
        print("\n📋 Traceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Este script se puede ejecutar desde el panel admin o directamente
    from main import app
    with app.app_context():
        limpiar_base_datos()
