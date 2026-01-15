"""
Script de Limpieza de Base de Datos
Limpia todos los datos excepto la estructura de tablas
Mantiene las credenciales de admin (están en variables de entorno)
"""
from models import db
from sqlalchemy import text, inspect

def limpiar_base_datos():
    """Limpia todos los datos de las tablas usando SQL directo para evitar problemas de foreign keys"""
    print("🧹 Iniciando limpieza de base de datos...")
    
    try:
        # Verificar qué tablas existen en la BD
        inspector = inspect(db.engine)
        tablas_existentes = inspector.get_table_names()
        print(f"📋 Tablas encontradas en BD: {', '.join(tablas_existentes)}")
        
        # Desactivar temporalmente las verificaciones de foreign keys (PostgreSQL)
        try:
            db.session.execute(text("SET session_replication_role = 'replica'"))
            print("  ✅ Verificaciones de foreign keys desactivadas temporalmente")
        except Exception as e:
            print(f"  ⚠️ No se pudieron desactivar foreign keys (puede ser SQLite): {e}")
        
        # Lista de tablas a limpiar (en orden para respetar foreign keys)
        # Primero las tablas dependientes, luego las principales
        tablas_a_limpiar = [
            'imagenes_vehiculos',
            'favoritos_vehiculos',
            'imagenes_negocios',
            'favoritos',
            'resenas',
            'mensajes',
            'ofertas',
            'noticias',
            'vehiculos',
            'agencias',
            'negocios',
            'usuarios'
        ]
        
        # Limpiar cada tabla usando SQL directo
        registros_eliminados_total = 0
        for tabla in tablas_a_limpiar:
            if tabla in tablas_existentes:
                print(f"  - Eliminando datos de {tabla}...")
                try:
                    # Contar registros antes de eliminar
                    count_before = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                    
                    if count_before > 0:
                        # Eliminar todos los registros
                        result = db.session.execute(text(f"DELETE FROM {tabla}"))
                        registros_eliminados = result.rowcount
                        registros_eliminados_total += registros_eliminados
                        print(f"    ✅ {registros_eliminados} registros eliminados de {tabla}")
                    else:
                        print(f"    ℹ️  {tabla} ya estaba vacía")
                except Exception as e:
                    print(f"    ❌ Error eliminando {tabla}: {e}")
                    import traceback
                    print(f"    📋 Traceback: {traceback.format_exc()}")
        
        # Opcional: Limpiar visitas (comentado por defecto para mantener analytics)
        if 'visitas' in tablas_existentes:
            print("  - Visitas: Manteniendo para analytics (no se eliminan)")
        
        # Reactivar verificaciones de foreign keys
        try:
            db.session.execute(text("SET session_replication_role = 'origin'"))
            print("  ✅ Verificaciones de foreign keys reactivadas")
        except Exception as e:
            print(f"  ⚠️ No se pudieron reactivar foreign keys: {e}")
        
        print(f"\n📊 Total de registros eliminados: {registros_eliminados_total}")
        
        # HACER COMMIT de todos los cambios
        print("\n💾 Guardando cambios en la base de datos...")
        try:
            db.session.commit()
            print("✅ Commit realizado exitosamente")
        except Exception as e:
            print(f"❌ Error al hacer commit: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            db.session.rollback()
            raise
        
        # Verificar que las tablas estén vacías DESPUÉS del commit
        print("\n🔍 Verificando limpieza (después de commit)...")
        errores_verificacion = []
        tablas_principales = ['usuarios', 'noticias', 'vehiculos', 'agencias', 'negocios']
        
        for tabla in tablas_principales:
            if tabla in tablas_existentes:
                try:
                    count = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                    print(f"  - {tabla}: {count} registros restantes")
                    if count > 0:
                        errores_verificacion.append(f"{tabla}: {count}")
                except Exception as e:
                    print(f"  - ⚠️ Error verificando {tabla}: {e}")
        
        if errores_verificacion:
            print(f"\n⚠️ ADVERTENCIA: Quedaron datos sin eliminar: {', '.join(errores_verificacion)}")
            print("   Reintentando eliminación directa...")
            for tabla_info in errores_verificacion:
                tabla = tabla_info.split(":")[0]
                try:
                    db.session.execute(text(f"TRUNCATE TABLE {tabla} CASCADE"))
                    print(f"   ✅ {tabla} truncada con CASCADE")
                except Exception as e:
                    try:
                        db.session.execute(text(f"DELETE FROM {tabla}"))
                        print(f"   ✅ {tabla} limpiada con DELETE")
                    except Exception as e2:
                        print(f"   ❌ Error limpiando {tabla}: {e2}")
            
            try:
                db.session.commit()
                print("   ✅ Commit final realizado después de limpieza adicional")
            except Exception as e:
                print(f"   ❌ Error en commit final: {e}")
        
        print("\n✅ Limpieza completada!")
        print(f"📊 Total de registros eliminados: {registros_eliminados_total}")
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
