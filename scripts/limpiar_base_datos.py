"""
Script de Limpieza de Base de Datos
Limpia todos los datos excepto la estructura de tablas
Mantiene las credenciales de admin (están en variables de entorno)
"""
from models import db
from sqlalchemy import text, inspect

def limpiar_base_datos():
    """Limpia todos los datos usando conexión directa con autocommit para forzar los cambios"""
    print("🧹 Iniciando limpieza de base de datos...")
    
    try:
        # Usar conexión directa con autocommit para forzar cambios inmediatos
        with db.engine.connect() as conn:
            # Activar autocommit en la conexión
            conn = conn.execution_options(autocommit=True)
            
            # Verificar qué tablas existen en la BD
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            print(f"📋 Tablas encontradas en BD: {', '.join(tablas_existentes)}")
            
            # Desactivar temporalmente las verificaciones de foreign keys (PostgreSQL)
            try:
                conn.execute(text("SET session_replication_role = 'replica'"))
                print("  ✅ Verificaciones de foreign keys desactivadas temporalmente")
            except Exception as e:
                print(f"  ⚠️ No se pudieron desactivar foreign keys (puede ser SQLite): {e}")
            
            # Lista de tablas a limpiar (en orden para respetar foreign keys)
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
            
            # Limpiar cada tabla usando conexión directa con autocommit
            registros_eliminados_total = 0
            for tabla in tablas_a_limpiar:
                if tabla in tablas_existentes:
                    print(f"  - Eliminando datos de {tabla}...")
                    try:
                        # Contar registros antes de eliminar
                        count_before = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                        print(f"    📊 Registros encontrados: {count_before}")
                        
                        if count_before > 0:
                            # Eliminar todos los registros (con autocommit activado)
                            result = conn.execute(text(f"DELETE FROM {tabla}"))
                            registros_eliminados = result.rowcount if hasattr(result, 'rowcount') else count_before
                            print(f"    ✅ {registros_eliminados} registros eliminados de {tabla} (autocommit)")
                            
                            # Verificar que se eliminaron (con nueva conexión para asegurar)
                            with db.engine.connect() as conn_verify:
                                count_after = conn_verify.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                                if count_after > 0:
                                    print(f"    ⚠️ ADVERTENCIA: Quedaron {count_after} registros después del DELETE")
                                    # Intentar TRUNCATE como último recurso
                                    try:
                                        conn_verify.execute(text(f"TRUNCATE TABLE {tabla} RESTART IDENTITY CASCADE"))
                                        conn_verify.commit()  # Commit explícito
                                        print(f"    ✅ {tabla} truncada con CASCADE y commit realizado")
                                        
                                        # Verificar de nuevo
                                        count_final = conn_verify.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                                        if count_final > 0:
                                            print(f"    ❌ ERROR: {tabla} aún tiene {count_final} registros después de TRUNCATE")
                                        else:
                                            print(f"    ✅ Verificado: {tabla} quedó completamente vacía")
                                    except Exception as e_truncate:
                                        print(f"    ❌ Error en TRUNCATE: {e_truncate}")
                                        import traceback
                                        print(f"    📋 Traceback: {traceback.format_exc()}")
                                else:
                                    print(f"    ✅ Verificado: {tabla} quedó vacía")
                            
                            registros_eliminados_total += registros_eliminados
                        else:
                            print(f"    ℹ️  {tabla} ya estaba vacía")
                    except Exception as e:
                        print(f"    ❌ Error eliminando {tabla}: {e}")
                        import traceback
                        print(f"    📋 Traceback: {traceback.format_exc()}")
                        # Continuar con la siguiente tabla
        
            # Opcional: Limpiar visitas (comentado por defecto para mantener analytics)
            if 'visitas' in tablas_existentes:
                print("  - Visitas: Manteniendo para analytics (no se eliminan)")
            
            # Reactivar verificaciones de foreign keys
            try:
                conn.execute(text("SET session_replication_role = 'origin'"))
                print("  ✅ Verificaciones de foreign keys reactivadas")
            except Exception as e:
                print(f"  ⚠️ No se pudieron reactivar foreign keys: {e}")
        
        print(f"\n📊 Total de registros eliminados: {registros_eliminados_total}")
        
        # Verificar que las tablas estén vacías DESPUÉS de la limpieza (con conexión nueva)
        print("\n🔍 Verificando limpieza final (con conexión nueva para asegurar cambios)...")
        errores_verificacion = []
        tablas_principales = ['usuarios', 'noticias', 'vehiculos', 'agencias', 'negocios']
        
        # Verificar con conexión completamente nueva
        with db.engine.connect() as conn_final:
            for tabla in tablas_principales:
                if tabla in tablas_existentes:
                    try:
                        count = conn_final.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                        print(f"  - {tabla}: {count} registros restantes")
                        if count > 0:
                            errores_verificacion.append(f"{tabla}: {count}")
                    except Exception as e:
                        print(f"  - ⚠️ Error verificando {tabla}: {e}")
        
        if errores_verificacion:
            print(f"\n⚠️ ADVERTENCIA: Quedaron datos sin eliminar: {', '.join(errores_verificacion)}")
            print("   Reintentando eliminación con TRUNCATE CASCADE usando conexión directa...")
            for tabla_info in errores_verificacion:
                tabla = tabla_info.split(":")[0]
                try:
                    # Usar conexión directa con autocommit para TRUNCATE
                    with db.engine.begin() as conn_truncate:  # begin() hace commit automático
                        conn_truncate.execute(text(f"TRUNCATE TABLE {tabla} RESTART IDENTITY CASCADE"))
                        print(f"   ✅ {tabla} truncada con CASCADE (commit automático)")
                        
                        # Verificar de nuevo
                        count_after = conn_truncate.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                        if count_after > 0:
                            print(f"   ❌ ERROR CRÍTICO: {tabla} aún tiene {count_after} registros después de TRUNCATE")
                        else:
                            print(f"   ✅ Verificado: {tabla} quedó completamente vacía")
                except Exception as e:
                    print(f"   ❌ Error en TRUNCATE de {tabla}: {e}")
                    import traceback
                    print(f"   📋 Traceback: {traceback.format_exc()}")
        
        print("\n✅ Limpieza completada!")
        print(f"📊 Total de registros eliminados: {registros_eliminados_total}")
        print("📝 Nota: Las credenciales de admin NO se perdieron (están en variables de entorno)")
        
        # Última verificación final
        if errores_verificacion:
            print("\n⚠️ RESUMEN: Algunas tablas aún tienen datos. Revisá los logs arriba para detalles.")
            return False
        else:
            print("\n✅ RESUMEN: Todas las tablas fueron limpiadas exitosamente.")
            return True
        
    except Exception as e:
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
