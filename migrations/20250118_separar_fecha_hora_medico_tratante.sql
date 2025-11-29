-- Migración: Separar fecha y hora en accidente_medico_tratante
-- Fecha: 2025-01-18
-- Descripción: Divide las columnas DateTime en columnas Date y Time separadas

-- 1. Agregar nuevas columnas de hora
ALTER TABLE accidente_medico_tratante 
ADD COLUMN hora_ingreso TIME COMMENT '81: hora de ingreso a IPS';

ALTER TABLE accidente_medico_tratante 
ADD COLUMN hora_egreso TIME COMMENT '83: hora de egreso de IPS';

-- 2. Migrar datos existentes (extraer hora de DateTime existente)
UPDATE accidente_medico_tratante 
SET hora_ingreso = TIME(fecha_ingreso) 
WHERE fecha_ingreso IS NOT NULL;

UPDATE accidente_medico_tratante 
SET hora_egreso = TIME(fecha_egreso) 
WHERE fecha_egreso IS NOT NULL;

-- 3. Convertir columnas de DateTime a Date
ALTER TABLE accidente_medico_tratante 
MODIFY COLUMN fecha_ingreso DATE COMMENT '80: fecha de ingreso a IPS';

ALTER TABLE accidente_medico_tratante 
MODIFY COLUMN fecha_egreso DATE COMMENT '82: fecha de egreso de IPS';

-- 4. Actualizar las fechas existentes (si quedaron con hora, convertir solo a fecha)
-- MySQL automáticamente convierte DATETIME a DATE truncando la parte de hora

-- Verificación
SELECT 
    id,
    fecha_ingreso,
    hora_ingreso,
    fecha_egreso,
    hora_egreso
FROM accidente_medico_tratante
LIMIT 5;
