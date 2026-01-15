"""
Script de Limpieza de Base de Datos
Limpia todos los datos excepto la estructura de tablas
Mantiene las credenciales de admin (están en variables de entorno)
"""
from models import db, Negocio, Usuario, Noticia, Resena, Oferta, Mensaje, ImagenNegocio, Visita, favoritos
from sqlalchemy import text

def limpiar_base_datos():
    """Limpia todos los datos de las tablas antiguas"""
    print("🧹 Iniciando limpieza de base de datos...")
    
    try:
        # Eliminar en orden (respetando foreign keys)
        print("  - Eliminando imágenes de negocios...")
        ImagenNegocio.query.delete()
        
        print("  - Eliminando favoritos...")
        db.session.execute(text("DELETE FROM favoritos"))
        
        print("  - Eliminando reseñas...")
        Resena.query.delete()
        
        print("  - Eliminando mensajes...")
        Mensaje.query.delete()
        
        print("  - Eliminando ofertas...")
        Oferta.query.delete()
        
        print("  - Eliminando noticias...")
        Noticia.query.delete()
        
        print("  - Eliminando negocios...")
        Negocio.query.delete()
        
        print("  - Limpiando usuarios (excepto admin si existe en BD)...")
        # Eliminar todos los usuarios (admin está en variables de entorno)
        Usuario.query.delete()
        
        print("  - Limpiando visitas (opcional - mantener para analytics)...")
        # Descomentar la siguiente línea si querés limpiar también las visitas
        # Visita.query.delete()
        
        # Commit de todos los cambios
        db.session.commit()
        
        print("✅ Limpieza completada exitosamente!")
        print("📝 Nota: Las credenciales de admin NO se perdieron (están en variables de entorno)")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error durante la limpieza: {e}")
        return False

if __name__ == "__main__":
    # Este script se puede ejecutar desde el panel admin o directamente
    from main import app
    with app.app_context():
        limpiar_base_datos()
