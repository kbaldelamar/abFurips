# 🔐 Control de Cambio de Propietario en Vehículos

## 📋 Problema Resuelto

Cuando se busca un vehículo existente en BD que tiene un propietario diferente al del accidente actual, el sistema debe:
1. Detectar el conflicto
2. Ofrecer opciones claras
3. Obligar al usuario a guardar el propietario ANTES de actualizar el vehículo

---

## ✅ Solución Implementada

### 🔍 **Al Buscar Vehículo por Placa:**

Sistema compara automáticamente:
- **Propietario registrado en BD** (del vehículo)
- **Propietario actual del accidente** (tab Propietario)

Si son DIFERENTES → Muestra modal con 3 opciones:

---

### 📊 **Modal de Decisión:**

```
⚠️ Conflicto de Propietarios
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El vehículo con placa 'ABC123' ya existe en la base de datos

📋 Propietario registrado en BD:
   • Nombre: Juan Pérez
   • Documento: 111111

📋 Propietario actual del accidente:
   • Nombre: María López
   • Documento: 222222

⚠️ ¿Qué desea hacer?

[Mantener propietario BD]  [Cambiar propietario]  [Cancelar]
```

---

### 🎯 **OPCIÓN 1: Mantener propietario BD**

**Comportamiento:**
- ✅ Asocia el vehículo al accidente ACTUAL
- ✅ El propietario en BD NO cambia (sigue siendo Juan Pérez)
- ✅ Permite guardar inmediatamente

**Uso:**
- Cuando el propietario real ES el que está en BD
- Error de captura: pusieron otro propietario por equivocación

**Resultado:**
```
Accidente → Vehículo: ABC123 → Propietario: Juan Pérez
```

---

### 🔄 **OPCIÓN 2: Cambiar propietario** (REQUIERE FLUJO)

**Comportamiento:**
1. ⚠️ Muestra mensaje instructivo
2. 🔒 **BLOQUEA el botón "Guardar Vehículo"**
3. 📝 Obliga a seguir este flujo:

**Flujo obligatorio:**
```
┌─────────────────────────────────────┐
│ PASO 1: Ir al tab PROPIETARIO      │
│ ✓ Completar datos de María López   │
│ ✓ Clic "Guardar Propietario"       │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ PASO 2: Regresar al tab VEHÍCULO   │
│ ✓ Botón "Guardar" ahora HABILITADO │
│ ✓ Clic "Guardar Vehículo"          │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ RESULTADO: Vehículo actualizado     │
│ 🔄 propietario_id actualizado en BD │
│ ABC123 → Ahora es de María López   │
└─────────────────────────────────────┘
```

**Validaciones automáticas:**

1. **Si intenta guardar SIN ir a Propietario:**
   ```
   ⚠️ Propietario no guardado
   
   Debe guardar el propietario primero
   
   Pasos:
   1. Vaya al tab Propietario
   2. Complete los datos
   3. Clic en Guardar Propietario
   4. Regrese al tab Vehículo
   5. Guarde el vehículo
   ```

2. **Si guarda el MISMO propietario que está en BD:**
   ```
   ⚠️ Propietario no cambió
   
   El propietario guardado es el mismo que está en BD
   
   Si desea cambiar el propietario:
   1. Vaya al tab Propietario
   2. Busque o ingrese OTRO propietario
   3. Guárdelo
   4. Regrese y guarde el vehículo
   ```

3. **Si todo está correcto:**
   ```
   ✅ Vehículo guardado exitosamente
   🔄 Propietario actualizado en BD:
      Juan Pérez → María López
   ```

---

### ❌ **OPCIÓN 3: Cancelar**

**Comportamiento:**
- ❌ No hace nada
- 🧹 Limpia el campo de búsqueda
- 📋 Muestra mensaje: "Búsqueda cancelada por el usuario"

---

## 🔧 Implementación Técnica

### Archivos Modificados:

#### 1. **vehiculo_presenter.py**

**Método: `buscar_vehiculo()`**
- Detecta conflicto de propietarios
- Muestra modal con 3 opciones
- Si elige "Cambiar propietario":
  - Marca: `self.view.vehiculo_cambiar_propietario = True`
  - Guarda: `self.view.vehiculo_propietario_bd = vehiculo.propietario_id`
  - Deshabilita: `self.view.btn_guardar.setEnabled(False)`

**Método: `guardar_vehiculo()`**
- Valida si `vehiculo_cambiar_propietario == True`
- Verifica que propietario esté guardado en BD
- Verifica que sea DIFERENTE al de BD
- Si OK: actualiza `vehiculo.propietario_id` y guarda

#### 2. **vehiculo_form.py**

**Variables de control:**
```python
self.vehiculo_cambiar_propietario = False
self.vehiculo_propietario_bd = None
```

**Método: `limpiar_formulario()`**
- Resetea variables de control

---

## 📊 Casos de Uso Completos

### Caso 1: Mantener propietario de BD

```
Usuario: Operador FURIPS
Situación: Vehículo ABC123 pertenece a Juan Pérez

1. Busca ABC123 en nuevo accidente
2. Sistema: "⚠️ Ya tiene propietario: Juan Pérez"
3. Elige: "Mantener propietario BD"
4. Guarda → Accidente asociado a ABC123
5. Propietario: Juan Pérez (sin cambios)

✅ CORRECTO: El vehículo sigue siendo de Juan
```

### Caso 2: Cambiar propietario (venta de vehículo)

```
Usuario: Operador FURIPS
Situación: ABC123 se vendió a María López

1. Busca ABC123 en nuevo accidente
2. Sistema: "⚠️ Propietario BD: Juan / Actual: María"
3. Elige: "Cambiar propietario"
4. Sistema: "📝 Primero guarde propietario"
5. Va a tab Propietario
6. Ingresa datos de María López
7. Guarda Propietario ✓
8. Regresa a tab Vehículo
9. Guarda Vehículo ✓
10. Sistema actualiza: ABC123 → María López

✅ CORRECTO: BD actualizada con nuevo propietario
```

### Caso 3: Error - Olvida guardar propietario

```
Usuario: Operador FURIPS

1. Busca ABC123
2. Elige: "Cambiar propietario"
3. NO va a tab Propietario
4. Intenta guardar vehículo
5. Sistema: "⚠️ Propietario no guardado"

❌ NO PERMITE GUARDAR hasta completar el flujo
```

### Caso 4: Error - Guarda mismo propietario

```
Usuario: Operador FURIPS

1. Busca ABC123 (propietario: Juan Pérez)
2. Elige: "Cambiar propietario"
3. Va a Propietario
4. Busca documento: 111111 (Juan Pérez)
5. Guarda
6. Regresa a Vehículo
7. Intenta guardar
8. Sistema: "⚠️ Propietario no cambió"

❌ NO PERMITE porque no tiene sentido
```

---

## 🎯 Beneficios

1. **🛡️ Integridad de Datos**: No se pueden hacer cambios inconsistentes
2. **📋 Flujo Claro**: Usuario sabe exactamente qué hacer
3. **⚠️ Prevención de Errores**: Validaciones automáticas
4. **👥 Responsabilidad Clara**: Cambios de propietario controlados
5. **📊 Auditoría**: Todos los cambios quedan registrados

---

## 🧪 Pruebas Recomendadas

### Prueba 1: Mantener propietario
```
✅ Buscar vehículo existente
✅ Elegir "Mantener propietario BD"
✅ Verificar que propietario NO cambió
✅ Verificar que accidente se asoció
```

### Prueba 2: Cambiar propietario (flujo completo)
```
✅ Buscar vehículo existente
✅ Elegir "Cambiar propietario"
✅ Verificar botón Guardar DESHABILITADO
✅ Ir a Propietario y guardar otro
✅ Regresar a Vehículo
✅ Verificar botón Guardar HABILITADO
✅ Guardar
✅ Verificar en BD que propietario_id cambió
```

### Prueba 3: Validación sin propietario guardado
```
✅ Buscar vehículo existente
✅ Elegir "Cambiar propietario"
✅ Intentar guardar SIN ir a Propietario
✅ Verificar mensaje de error
✅ Verificar que NO guardó
```

### Prueba 4: Validación mismo propietario
```
✅ Buscar vehículo existente (prop: Juan)
✅ Elegir "Cambiar propietario"
✅ Ir a Propietario
✅ Buscar y guardar Juan (mismo)
✅ Regresar e intentar guardar
✅ Verificar mensaje: "Propietario no cambió"
```

---

**Fecha de Implementación**: 2025-11-18  
**Versión**: 2.0  
**Estado**: ✅ Completado y Validado
