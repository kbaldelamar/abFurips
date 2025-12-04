"""
Verificar estructura de la tabla vehiculo
"""
import sys
sys.path.insert(0, 'c:/python/abFurips')

from app.config.db import get_engine_app
from sqlalchemy import text


def verificar_estructura():
    """Verifica la estructura de la tabla vehiculo."""
    engine = get_engine_app()
    
    with engine.connect() as conn:
        # Describir tabla vehiculo
        result = conn.execute(text("DESCRIBE vehiculo"))
        rows = result.fetchall()
        
        print("\n" + "="*110)
        print("ESTRUCTURA DE LA TABLA VEHICULO")
        print("="*110)
        print(f"{'Campo':<30} {'Tipo':<25} {'Null':<8} {'Key':<8} {'Default':<15} {'Extra':<20}")
        print("-"*110)
        
        for row in rows:
            campo, tipo, null, key, default, extra = row
            default_str = str(default) if default is not None else 'NULL'
            print(f"{campo:<30} {tipo:<25} {null:<8} {key:<8} {default_str:<15} {extra:<20}")
        
        print("="*110)
        
        # Verificar específicamente el campo estado
        has_estado = any(row[0] == 'estado' for row in rows)
        
        if has_estado:
            print("\n✅ El campo 'estado' EXISTE en la tabla vehiculo")
            
            # Contar registros por estado
            result = conn.execute(text("SELECT estado, COUNT(*) FROM vehiculo GROUP BY estado"))
            estados = result.fetchall()
            
            print("\n📊 Distribución de estados:")
            for estado, count in estados:
                estado_texto = "ACTIVO" if estado == 1 else "INACTIVO"
                print(f"   - {estado_texto} (estado={estado}): {count} vehículo(s)")
        else:
            print("\n❌ El campo 'estado' NO EXISTE en la tabla vehiculo")
            print("   Ejecutar: ALTER TABLE `vehiculo` ADD COLUMN `estado` TINYINT(1) NOT NULL DEFAULT 1...")
        
        print()


if __name__ == "__main__":
    verificar_estructura()
