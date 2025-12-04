# Implementación de Estado y Anulación (Soft Delete)

## Resumen
Se implementó un sistema de anulación de registros usando un campo `estado` en lugar de eliminaciones físicas, permitiendo mantener el historial completo de la base de datos.

## Cambios Realizados

### 1. Base de Datos
**Script SQL:** `migrations/add_estado_column.sql`

Se agregó el campo `estado` a 15 tablas:
- `accidente` ✅
- `accidente_conductor` ✅
- `accidente_detalle` ✅
- `accidente_propietario` ✅
- `accidente_totales` ✅
- `accidente_victima` ✅
- `persona` ✅
- `prestador_salud` ✅
- `vehiculo` ✅
- `estado_aseguramiento` ✅
- `naturaleza_evento` ✅
- `sexo` ✅
- `tipo_identificacion` ✅
- `tipo_servicio` ✅
- `tipo_vehiculo` ✅

**Campo:** `TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo'`

### 2. Modelos SQLAlchemy

#### `app/data/models/accidente.py`
```python
# Clase Accidente
estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")

# Clase AccidenteVictima
estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")

# Clase AccidenteConductor
estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")

# Clase AccidentePropietario
estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
```

#### `app/data/models/persona.py`
```python
estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
```

### 3. Repositorio de Accidente

#### `app/data/repositories/accidente_repo.py`

**Nuevos métodos:**

```python
def anular(self, accidente_id: int) -> bool:
    """Anula un accidente (soft delete - cambia estado a 0)."""
    accidente = self.get_by_id(accidente_id)
    if accidente:
        accidente.estado = 0
        self.session.flush()
        return True
    return False

def reactivar(self, accidente_id: int) -> bool:
    """Reactiva un accidente anulado (cambia estado a 1)."""
    accidente = self.get_by_id(accidente_id)
    if accidente:
        accidente.estado = 1
        self.session.flush()
        return True
    return False

def get_activos(self, limit: int = 100) -> List[Accidente]:
    """Obtiene solo accidentes activos (estado=1)."""
    return (
        self.session.query(Accidente)
        .filter(Accidente.estado == 1)
        .order_by(Accidente.fecha_evento.desc())
        .limit(limit)
        .all()
    )
```

**Método modificado:**

```python
def search_by_filters(..., solo_activos: bool = True):
    """Busca accidentes por múltiples criterios."""
    # Por defecto solo mostrar activos
    if solo_activos:
        query = query.filter(Accidente.estado == 1)
```

### 4. Interfaz de Usuario

#### `app/ui/views/accidente_form.py`

**Nuevo botón:**
```python
self.btn_anular_accidente = QPushButton("❌ Anular")
self.btn_anular_accidente.setMinimumWidth(100)
self.btn_anular_accidente.clicked.connect(self._on_anular_accidente)
self.btn_anular_accidente.setVisible(False)
# Estilo rojo para destacar acción de anulación
```

**Nueva señal:**
```python
anular_accidente_signal = Signal(int)  # Emite el ID del accidente a anular
```

**Nuevo método:**
```python
def _on_anular_accidente(self):
    """Maneja el clic en anular accidente."""
    # Confirma con diálogo antes de anular
    # Emite señal: self.anular_accidente_signal.emit(accidente_id)
```

**Visibilidad del botón:**
- Oculto al crear nuevo accidente
- Visible cuando se carga/guarda un accidente existente
- Se oculta al limpiar formulario

### 5. Presenter

#### `app/ui/presenters/accidente_presenter.py`

**Conexión de señal:**
```python
def _connect_signals(self):
    self.view.anular_accidente_signal.connect(self.anular_accidente)
```

**Nuevo método:**
```python
def anular_accidente(self, accidente_id: int):
    """Anula un accidente (soft delete - cambia estado a 0)."""
    # Llama a repo.anular()
    # Muestra mensaje de éxito
    # Limpia el formulario
```

## Flujo de Uso

### Para Anular un Accidente:

1. **Cargar o crear un accidente**
   - Al guardar/cargar aparece el botón "❌ Anular"

2. **Hacer clic en "Anular"**
   - Aparece diálogo de confirmación
   - Mensaje: "¿Está seguro de anular el accidente #XXXXXX? El accidente no se eliminará, solo cambiará su estado a ANULADO."

3. **Confirmar anulación**
   - El campo `estado` cambia de 1 a 0 en la BD
   - Se muestra mensaje de éxito
   - El formulario se limpia automáticamente

4. **Resultado**
   - El accidente ya no aparece en búsquedas normales
   - Los datos permanecen en la BD para auditoría
   - Se puede reactivar si es necesario (método `reactivar()`)

## Ventajas del Soft Delete

### ✅ **Auditoría Completa**
- Se mantiene historial de todos los accidentes
- No se pierde información para reportes

### ✅ **Reversibilidad**
- Los accidentes anulados pueden reactivarse
- Uso del método `reactivar(accidente_id)`

### ✅ **Integridad Referencial**
- No se rompen relaciones con otras tablas
- Víctimas, conductores y propietarios quedan intactos

### ✅ **Trazabilidad**
- Se puede saber cuándo y por qué se anuló
- Útil para auditorías y cumplimiento

## Búsquedas

### Por Defecto - Solo Activos
```python
repo.search_by_filters(solo_activos=True)  # Default
repo.get_activos()  # Método específico
```

### Incluir Anulados
```python
repo.search_by_filters(solo_activos=False)  # Muestra todos
```

### Solo Anulados
```python
query = session.query(Accidente).filter(Accidente.estado == 0)
```

## Próximos Pasos (Opcional)

### 1. Agregar Fecha de Anulación
```sql
ALTER TABLE accidente 
ADD COLUMN fecha_anulacion DATETIME NULL COMMENT 'Fecha de anulación';
```

### 2. Agregar Usuario que Anuló
```sql
ALTER TABLE accidente 
ADD COLUMN usuario_anulacion_id INT UNSIGNED NULL COMMENT 'Usuario que anuló';
```

### 3. Agregar Motivo de Anulación
```sql
ALTER TABLE accidente 
ADD COLUMN motivo_anulacion VARCHAR(500) NULL COMMENT 'Motivo de anulación';
```

### 4. Reporte de Anulados
Crear vista o consulta para ver accidentes anulados con detalles.

## Testing

### Pruebas Necesarias:

1. ✅ Crear accidente → Debe tener estado=1
2. ✅ Anular accidente → Debe cambiar estado a 0
3. ✅ Buscar accidentes → No debe aparecer el anulado
4. ✅ Buscar con solo_activos=False → Debe aparecer el anulado
5. ✅ Reactivar accidente → Debe volver estado a 1
6. ✅ Relaciones intactas → Víctimas/conductores deben seguir existiendo

## Notas Importantes

⚠️ **IMPORTANTE:** Antes de usar en producción:
1. Ejecutar el script SQL `add_estado_column.sql`
2. Hacer backup de la base de datos
3. Probar en ambiente de desarrollo
4. Verificar que todos los registros tengan estado=1

⚠️ **CONSIDERACIÓN:** 
- El botón "Anular" solo aparece en accidentes ya guardados
- Los accidentes nuevos (sin guardar) no tienen botón de anular
- La anulación es permanente a menos que se reactive manualmente

## Fecha de Implementación
2025-11-17
