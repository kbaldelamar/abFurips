#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migración: Crear tablas de auditoría para vehículos y propietarios
Fecha: 2025-11-18
Descripción: Crea vehiculo_historial y propietario_historial para trazabilidad
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import text
from app.config.db import get_engine_app

def ejecutar_migracion():
    """Ejecuta la migración de auditoría."""
    print("=" * 60)
    print("MIGRACIÓN: Crear tablas de auditoría")
    print("=" * 60)
    
    try:
        # Configurar conexión
        engine = get_engine_app()
        
        with engine.connect() as conn:
            print("\n✓ Conexión exitosa a la base de datos")
            
            # Verificar si las tablas ya existen
            print("\n📋 Verificando tablas existentes...")
            
            result_vh = conn.execute(text(
                "SHOW TABLES LIKE 'vehiculo_historial'"
            ))
            vh_exists = result_vh.fetchone() is not None
            
            result_ph = conn.execute(text(
                "SHOW TABLES LIKE 'propietario_historial'"
            ))
            ph_exists = result_ph.fetchone() is not None
            
            if vh_exists and ph_exists:
                print("⚠️  Las tablas de auditoría ya existen")
                print("   - vehiculo_historial: ✓")
                print("   - propietario_historial: ✓")
                return
            
            # Crear tabla vehiculo_historial
            if not vh_exists:
                print("\n📝 Creando tabla vehiculo_historial...")
                conn.execute(text("""
                    CREATE TABLE `vehiculo_historial` (
                      `id` INT(11) NOT NULL AUTO_INCREMENT,
                      `accidente_id` INT(11) NOT NULL COMMENT 'ID del accidente relacionado',
                      `vehiculo_id_anterior` INT(11) DEFAULT NULL COMMENT 'ID del vehículo anulado (si aplica)',
                      `vehiculo_id_nuevo` INT(11) DEFAULT NULL COMMENT 'ID del nuevo vehículo creado (si aplica)',
                      `accion` VARCHAR(50) NOT NULL COMMENT 'ANULAR, CREAR, ACTUALIZAR',
                      `placa_anterior` VARCHAR(10) DEFAULT NULL COMMENT 'Placa del vehículo anulado',
                      `placa_nueva` VARCHAR(10) DEFAULT NULL COMMENT 'Placa del nuevo vehículo',
                      `motivo` VARCHAR(500) DEFAULT NULL COMMENT 'Motivo del cambio',
                      `usuario` VARCHAR(100) DEFAULT NULL COMMENT 'Usuario que realizó el cambio',
                      `fecha_cambio` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`),
                      KEY `idx_accidente` (`accidente_id`),
                      KEY `idx_vehiculo_anterior` (`vehiculo_id_anterior`),
                      KEY `idx_vehiculo_nuevo` (`vehiculo_id_nuevo`),
                      KEY `idx_fecha` (`fecha_cambio`),
                      KEY `idx_vh_placa_anterior` (`placa_anterior`),
                      KEY `idx_vh_placa_nueva` (`placa_nueva`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='Auditoría de cambios en vehículos asociados a accidentes'
                """))
                print("   ✓ Tabla vehiculo_historial creada exitosamente")
            else:
                print("   ⏭️  vehiculo_historial ya existe, omitiendo...")
            
            # Crear tabla propietario_historial
            if not ph_exists:
                print("\n📝 Creando tabla propietario_historial...")
                conn.execute(text("""
                    CREATE TABLE `propietario_historial` (
                      `id` INT(11) NOT NULL AUTO_INCREMENT,
                      `accidente_id` INT(11) NOT NULL COMMENT 'ID del accidente relacionado',
                      `propietario_id_anterior` INT(11) DEFAULT NULL COMMENT 'ID del propietario anulado (si aplica)',
                      `propietario_id_nuevo` INT(11) DEFAULT NULL COMMENT 'ID del nuevo propietario creado (si aplica)',
                      `persona_id_anterior` INT(11) DEFAULT NULL COMMENT 'ID de la persona del propietario anulado',
                      `persona_id_nueva` INT(11) DEFAULT NULL COMMENT 'ID de la persona del nuevo propietario',
                      `accion` VARCHAR(50) NOT NULL COMMENT 'ANULAR, CREAR, ACTUALIZAR',
                      `documento_anterior` VARCHAR(20) DEFAULT NULL COMMENT 'Documento del propietario anulado',
                      `documento_nuevo` VARCHAR(20) DEFAULT NULL COMMENT 'Documento del nuevo propietario',
                      `motivo` VARCHAR(500) DEFAULT NULL COMMENT 'Motivo del cambio',
                      `usuario` VARCHAR(100) DEFAULT NULL COMMENT 'Usuario que realizó el cambio',
                      `fecha_cambio` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`),
                      KEY `idx_accidente` (`accidente_id`),
                      KEY `idx_propietario_anterior` (`propietario_id_anterior`),
                      KEY `idx_propietario_nuevo` (`propietario_id_nuevo`),
                      KEY `idx_fecha` (`fecha_cambio`),
                      KEY `idx_ph_documento_anterior` (`documento_anterior`),
                      KEY `idx_ph_documento_nuevo` (`documento_nuevo`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='Auditoría de cambios en propietarios asociados a accidentes'
                """))
                print("   ✓ Tabla propietario_historial creada exitosamente")
            else:
                print("   ⏭️  propietario_historial ya existe, omitiendo...")
            
            # Commit
            conn.commit()
            
            # Verificar estructura
            print("\n📊 Verificando estructura de tablas...")
            
            if not vh_exists:
                result = conn.execute(text("DESCRIBE vehiculo_historial"))
                print("\n🔍 vehiculo_historial:")
                for row in result:
                    print(f"   - {row[0]}: {row[1]}")
            
            if not ph_exists:
                result = conn.execute(text("DESCRIBE propietario_historial"))
                print("\n🔍 propietario_historial:")
                for row in result:
                    print(f"   - {row[0]}: {row[1]}")
            
            print("\n" + "=" * 60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print("\n📝 Ahora el sistema registrará automáticamente:")
            print("   - Anulaciones de vehículos y propietarios")
            print("   - Creación de nuevos registros")
            print("   - Usuario y fecha de cada cambio")
            print("   - Trazabilidad completa para auditoría")
            
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_migracion()
