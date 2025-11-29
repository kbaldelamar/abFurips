"""
Script de migración: Agregar campo 'estado' a tabla vehiculo
Fecha: 2025-11-17
Propósito: Habilitar soft delete en vehículos
"""
from sqlalchemy import text
from app.config.db import get_engine_app


def run_migration():
    """Ejecuta la migración para agregar campo estado a vehiculo."""
    
    engine = get_engine_app()
    
    # SQL de migración
    alter_sql = """
    ALTER TABLE `vehiculo` 
    ADD COLUMN `estado` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo' AFTER `propietario_id`;
    """
    
    update_sql = """
    UPDATE `vehiculo` SET `estado` = 1;
    """
    
    verify_sql = """
    SELECT 
        COUNT(*) as total_vehiculos, 
        estado 
    FROM vehiculo 
    GROUP BY estado;
    """
    
    try:
        with engine.connect() as conn:
            # Verificar si la columna ya existe
            check_column = text("""
                SELECT COUNT(*) as existe 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'vehiculo' 
                AND COLUMN_NAME = 'estado';
            """)
            
            result = conn.execute(check_column)
            existe = result.fetchone()[0]
            
            if existe > 0:
                print("⚠️  La columna 'estado' ya existe en la tabla 'vehiculo'")
                print("✓  No se requiere migración")
                return True
            
            print("📝 Ejecutando migración...")
            print("   1. Agregando columna 'estado' a tabla 'vehiculo'...")
            
            # Ejecutar ALTER TABLE
            conn.execute(text(alter_sql))
            conn.commit()
            print("   ✓ Columna agregada exitosamente")
            
            print("   2. Actualizando registros existentes a estado=1...")
            # Ejecutar UPDATE
            result = conn.execute(text(update_sql))
            conn.commit()
            print(f"   ✓ {result.rowcount} registros actualizados")
            
            print("   3. Verificando resultados...")
            # Verificar
            result = conn.execute(text(verify_sql))
            rows = result.fetchall()
            
            print("\n📊 RESUMEN:")
            print("   Estado de vehículos:")
            for row in rows:
                estado_texto = "ACTIVO" if row[1] == 1 else "INACTIVO"
                print(f"   - {estado_texto} (estado={row[1]}): {row[0]} vehículo(s)")
            
            print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR en la migración: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar campo 'estado' a tabla vehiculo")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    print("=" * 60)
    if success:
        print("MIGRACIÓN FINALIZADA CORRECTAMENTE")
    else:
        print("MIGRACIÓN FALLÓ - Revisar errores arriba")
    print("=" * 60)
