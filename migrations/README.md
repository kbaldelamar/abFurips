# Migración: Agregar campo 'estado' a todas las tablas

## Descripción
Este script agrega un campo `estado` (TINYINT) a todas las tablas de la base de datos FURIPS que no lo tienen actualmente.

**Valores del campo:**
- `1` = Activo (por defecto)
- `0` = Inactivo

## Tablas Afectadas (15 tablas)

### Tablas principales:
1. `accidente`
2. `accidente_conductor`
3. `accidente_detalle`
4. `accidente_propietario`
5. `accidente_totales`
6. `accidente_victima`
7. `persona`
8. `prestador_salud`
9. `vehiculo`

### Tablas de catálogo:
10. `estado_aseguramiento`
11. `naturaleza_evento`
12. `sexo`
13. `tipo_identificacion`
14. `tipo_servicio`
15. `tipo_vehiculo`

## Tablas que YA tienen estado (no se modifican)

- `departamento` - Ya tiene campo `estado`
- `municipio` - Ya tiene campo `estado`
- `pais` - Ya tiene campo `estado`
- `procedimiento` - Tiene campo `estado` tipo ENUM

## Instrucciones de Uso

### Opción 1: Ejecutar desde terminal (recomendado)

```bash
# Conectar a MariaDB
mysql -u root -p furips < migrations/add_estado_column.sql
```

### Opción 2: Ejecutar desde MySQL Workbench / HeidiSQL / SQLyog

1. Abrir el archivo `add_estado_column.sql`
2. Conectar a la base de datos `furips`
3. Ejecutar todo el script

### Opción 3: Copiar y pegar en terminal MySQL

```sql
USE furips;
SOURCE c:/python/abFurips/migrations/add_estado_column.sql;
```

## Verificar los Cambios

Después de ejecutar el script, verifica que todas las tablas tengan el campo:

```sql
-- Ver estructura de una tabla
DESCRIBE accidente;

-- Verificar que todos los registros tengan estado = 1
SELECT COUNT(*) FROM accidente WHERE estado = 1;
SELECT COUNT(*) FROM persona WHERE estado = 1;
```

## Rollback

Si necesitas revertir los cambios, ejecuta el script de rollback:

```bash
mysql -u root -p furips < migrations/rollback_estado_column.sql
```

⚠️ **ADVERTENCIA:** El rollback eliminará el campo `estado` de todas las tablas. Úsalo solo si es absolutamente necesario.

## Impacto en la Aplicación

### Cambios Necesarios en el Código Python

Después de ejecutar este script, necesitarás actualizar los modelos SQLAlchemy para incluir el campo `estado`:

**Ejemplo para el modelo Persona:**

```python
# En app/data/models.py
class Persona(Base):
    __tablename__ = "persona"
    
    id = Column(BigInteger, primary_key=True)
    # ... otros campos ...
    estado = Column(TINYINT(1), nullable=False, default=1, comment="1 activo, 0 inactivo")
```

### Actualizar Repositorios

Modifica los métodos `get_all()` para filtrar solo registros activos:

```python
# Ejemplo en persona_repo.py
def get_all_activos(self) -> List[Persona]:
    """Obtiene todas las personas activas."""
    return self.session.query(Persona).filter(Persona.estado == 1).all()
```

### Soft Delete

Ahora puedes implementar "eliminación suave" cambiando el estado a 0 en lugar de eliminar físicamente:

```python
def desactivar_persona(self, persona_id: int) -> bool:
    """Desactiva una persona (soft delete)."""
    persona = self.get_by_id(persona_id)
    if persona:
        persona.estado = 0
        self.session.commit()
        return True
    return False
```

## Notas Importantes

1. ✅ **Backup:** Siempre haz un backup de la base de datos antes de ejecutar migraciones
2. ✅ **Testing:** Prueba primero en un ambiente de desarrollo
3. ✅ **Todos los registros existentes se marcan como activos (estado=1)** por defecto
4. ✅ **El campo es NOT NULL con DEFAULT 1** - no afecta inserts futuros
5. ✅ **Compatible con la estructura actual** - no rompe foreign keys ni constraints

## Fecha de Creación
2025-11-17

## Autor
Sistema FURIPS Desktop v1.0.0
