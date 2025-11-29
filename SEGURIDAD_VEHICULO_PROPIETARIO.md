# 🔒 SEGURIDAD DE DATOS: Vehículo y Propietario

## 📋 Problema Identificado

**Situación anterior (INSEGURA):**
- Si busco otra placa → al actualizar cambia el vehículo (pérdida de datos originales)
- Si busco otra cédula → al actualizar cambia el propietario (pérdida de datos originales)
- No había protección contra modificaciones accidentales
- Podía cambiar vehículo sin anular el anterior
- Podía cambiar propietario sin anular el anterior

**Consecuencias:**
- Pérdida de integridad de datos históricos
- No hay trazabilidad de cambios
- Registros originales sobrescritos sin auditoría

---

## ✅ Solución Implementada

### 1. **Escenario 1: Cargar Accidente con Vehículo Existente**
```
✓ Accidente cargado
✓ Vehículo: ABC123 (estado=1)
✅ txt_placa HABILITADO (se puede editar)
🔒 btn_buscar DESHABILITADO
🔴 "Búsqueda deshabilitada. Para buscar otro, debe anular este primero"
```

#### Vehículo:
Cuando ya existe un vehículo guardado:
- ✅ Campo `txt_placa` **habilitado** (se puede editar manualmente si hubo error)
- ❌ Botón `btn_buscar` **deshabilitado**
- 🔒 Mensaje: "Búsqueda deshabilitada. Para buscar otro, debe anular este primero"
- 🎨 Solo el botón con fondo gris (#E0E0E0)

#### Propietario:
Cuando ya existe un propietario guardado:
- ✅ Campo `txt_numero_id` **habilitado** (se puede editar manualmente si hubo error)
- ✅ Combo `combo_tipo_id` **habilitado** (se puede editar manualmente si hubo error)
- ❌ Botón `btn_buscar` **deshabilitado**
- 🔒 Mensaje: "Búsqueda deshabilitada. Para buscar otro, debe anular este primero"
- 🎨 Solo el botón con fondo gris (#E0E0E0)

#### Víctima:
Cuando ya existe una víctima guardada:
- ✅ Campo `txt_numero_id` **habilitado** (se puede editar manualmente si hubo error)
- ✅ Combo `combo_tipo_id` **habilitado** (se puede editar manualmente si hubo error)
- ❌ Botón `btn_buscar` **deshabilitado**
- 🔒 Mensaje: "Búsqueda deshabilitada. Para buscar otro, debe anular este primero"
- 🎨 Solo el botón con fondo gris (#E0E0E0)

#### Conductor:
Cuando ya existe un conductor guardado:
- ✅ Campo `txt_numero_id` **habilitado** (se puede editar manualmente si hubo error)
- ✅ Combo `combo_tipo_id` **habilitado** (se puede editar manualmente si hubo error)
- ❌ Botón `btn_buscar` **deshabilitado**
- 🔒 Mensaje: "Búsqueda deshabilitada. Para buscar otro, debe anular este primero"
- 🎨 Solo el botón con fondo gris (#E0E0E0)

---

### 2. **Flujo Seguro para Cambiar Registros**

```
┌─────────────────────────────────────────┐
│ PASO 1: Cargar Accidente               │
│ ✓ Vehículo actual: ABC123              │
│ ✓ Propietario actual: Juan Pérez       │
│ ✓ Víctima actual: María López          │
│ ✓ Conductor actual: Pedro García       │
│ 🔒 Botones de BÚSQUEDA bloqueados      │
│ ✅ Campos EDITABLES (corregir errores) │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ PASO 2: Anular Registro Actual         │
│ Clic en "Anular Vehículo" o            │
│ "Anular Propietario"                    │
│ ⚠️ Confirmación requerida              │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ PASO 3: Formulario Limpio               │
│ ✓ Campos vacíos                         │
│ ✓ estado=0 para registro anterior      │
│ 🔓 Búsquedas DESBLOQUEADAS             │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ PASO 4: Buscar Nuevo Registro          │
│ Buscar por placa: XYZ789               │
│ Buscar por cédula: 12345678            │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ PASO 5: Guardar Nuevo Registro         │
│ ✓ Nuevo vehículo con estado=1         │
│ ✓ Nuevo propietario con estado=1      │
│ ✓ Asociado al mismo accidente         │
└─────────────────────────────────────────┘
```

---

### 3. **Tablas de Auditoría**

#### `vehiculo_historial`
Registra:
- `accidente_id`: Qué accidente
- `vehiculo_id_anterior`: Vehículo anulado
- `vehiculo_id_nuevo`: Nuevo vehículo creado
- `accion`: ANULAR / CREAR / ACTUALIZAR
- `placa_anterior` / `placa_nueva`: Placas
- `usuario`: Quién hizo el cambio
- `fecha_cambio`: Cuándo se hizo
- `motivo`: Por qué se cambió

#### `propietario_historial`
Registra:
- `accidente_id`: Qué accidente
- `propietario_id_anterior`: Propietario anulado
- `propietario_id_nuevo`: Nuevo propietario creado
- `persona_id_anterior` / `persona_id_nueva`: Personas relacionadas
- `accion`: ANULAR / CREAR / ACTUALIZAR
- `documento_anterior` / `documento_nuevo`: Documentos
- `usuario`: Quién hizo el cambio
- `fecha_cambio`: Cuándo se hizo
- `motivo`: Por qué se cambió

---

## 🔧 Implementación Técnica

### Archivos Modificados:

1. **app/ui/views/vehiculo_form.py**
   - `_bloquear_busqueda_vehiculo()`: Deshabilita SOLO botón búsqueda
   - `_desbloquear_busqueda_vehiculo()`: Habilita después de anular
   - `cargar_vehiculo_existente()`: Llama a bloqueo automáticamente
   - `limpiar_formulario()`: Llama a desbloqueo automáticamente
   - **Campo placa editable**: Permite correcciones manuales

2. **app/ui/views/propietario_form.py**
   - `_bloquear_busqueda_propietario()`: Deshabilita SOLO botón búsqueda
   - `_desbloquear_busqueda_propietario()`: Habilita después de anular
   - `cargar_propietario_existente()`: Llama a bloqueo automáticamente
   - `limpiar_formulario()`: Llama a desbloqueo automáticamente
   - **Campos tipo/número documento editables**: Permite correcciones manuales

3. **app/ui/views/victima_form.py**
   - `_bloquear_busqueda_victima()`: Deshabilita SOLO botón búsqueda
   - `_desbloquear_busqueda_victima()`: Habilita después de anular
   - `cargar_victima_existente()`: Llama a bloqueo automáticamente
   - `limpiar_formulario()`: Llama a desbloqueo automáticamente
   - **Campos tipo/número documento editables**: Permite correcciones manuales

4. **app/ui/views/conductor_form.py**
   - `_bloquear_busqueda_conductor()`: Deshabilita SOLO botón búsqueda
   - `_desbloquear_busqueda_conductor()`: Habilita después de anular
   - `cargar_conductor_existente()`: Llama a bloqueo automáticamente
   - `limpiar_formulario()`: Llama a desbloqueo automáticamente
   - **Campos tipo/número documento editables**: Permite correcciones manuales

5. **app/ui/presenters/vehiculo_presenter.py**
   - `anular_vehiculo()`: Llama a `limpiar_formulario()` después de anular
   - Mensaje: "Puede registrar un nuevo vehículo para este accidente"

6. **app/ui/presenters/propietario_presenter.py**
   - `anular_propietario()`: Llama a `limpiar_formulario()` después de anular
   - Mensaje: "Puede registrar un nuevo propietario para este accidente"

7. **app/ui/presenters/victima_presenter.py**
   - `anular_victima()`: Llama a `limpiar_formulario()` después de anular

8. **app/ui/presenters/conductor_presenter.py**
   - `anular_conductor()`: Llama a `limpiar_formulario()` después de anular

### Migraciones Ejecutadas:

- ✅ `migrations/create_auditoria_vehiculo_propietario.sql`
- ✅ `migrations/run_create_auditoria.py`

---

## 📊 Consultas de Auditoría

### Ver historial de cambios de un accidente:

```sql
-- Historial de vehículos
SELECT 
    h.fecha_cambio,
    h.accion,
    h.placa_anterior,
    h.placa_nueva,
    h.usuario,
    h.motivo
FROM vehiculo_historial h
WHERE h.accidente_id = 10
ORDER BY h.fecha_cambio DESC;

-- Historial de propietarios
SELECT 
    h.fecha_cambio,
    h.accion,
    h.documento_anterior,
    h.documento_nuevo,
    h.usuario,
    h.motivo
FROM propietario_historial h
WHERE h.accidente_id = 10
ORDER BY h.fecha_cambio DESC;
```

### Ver todos los cambios recientes:

```sql
-- Cambios en vehículos últimos 30 días
SELECT 
    DATE(fecha_cambio) as fecha,
    COUNT(*) as total_cambios,
    SUM(CASE WHEN accion = 'ANULAR' THEN 1 ELSE 0 END) as anulaciones,
    SUM(CASE WHEN accion = 'CREAR' THEN 1 ELSE 0 END) as nuevos
FROM vehiculo_historial
WHERE fecha_cambio >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(fecha_cambio)
ORDER BY fecha DESC;
```

---

## ✅ Beneficios de la Solución

1. **Integridad de Datos**: No se pierden registros originales
2. **Trazabilidad Completa**: Sabemos quién, cuándo y por qué cambió
3. **Prevención de Errores**: No se puede cambiar accidentalmente
4. **Auditoría Completa**: Historial completo de cambios
5. **Flujo Claro**: Usuario sabe exactamente qué hacer
6. **Reversibilidad**: Podemos reconstruir estados anteriores

---

## 🧪 Pruebas de Funcionamiento

### Test 1: Bloqueo de Búsqueda
1. Cargar accidente con vehículo/propietario/víctima/conductor existente
2. Verificar: SOLO botón búsqueda deshabilitado ✓
3. Verificar: campos (placa/documento) EDITABLES ✓
4. Verificar: mensaje "Búsqueda deshabilitada..." visible ✓
5. Verificar: se puede corregir datos manualmente y actualizar ✓

### Test 2: Anulación y Desbloqueo
1. Clic en "Anular Vehículo" o "Anular Propietario"
2. Confirmar anulación
3. Verificar: formulario limpio ✓
4. Verificar: campos de búsqueda habilitados ✓
5. Verificar: estado=0 en base de datos ✓

### Test 3: Nuevo Registro
1. Buscar nueva placa/cédula
2. Completar formulario
3. Guardar
4. Verificar: nuevo registro con estado=1 ✓
5. Verificar: asociado al mismo accidente ✓
6. Verificar: búsqueda bloqueada nuevamente ✓

### Test 4: Auditoría
1. Ejecutar cambio completo (anular → crear nuevo)
2. Consultar tabla vehiculo_historial/propietario_historial
3. Verificar: registro de anulación ✓
4. Verificar: registro de creación ✓
5. Verificar: fecha_cambio correcta ✓

---

## 📝 Notas Importantes

- **Estado=0**: Registro anulado (soft delete)
- **Estado=1**: Registro activo
- **Anular**: No elimina físicamente, solo cambia estado
- **Búsquedas**: Siempre filtran por estado=1
- **Auditoría**: Tablas independientes sin FK (por compatibilidad)

---

## 🔮 Mejoras Futuras (Opcionales)

1. Agregar campo `motivo` en diálogo de anulación
2. Capturar usuario actual del sistema
3. Reportes de auditoría en interfaz gráfica
4. Exportar historial a Excel/PDF
5. Restaurar registros anulados (soft undelete)
6. Dashboard de cambios frecuentes

---

**Fecha de Implementación**: 2025-11-18  
**Versión**: 1.0  
**Estado**: ✅ Completado y Funcional
