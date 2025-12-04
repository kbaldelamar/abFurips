WITH setAccidente AS (

SELECT
accidente.`id` idAccidente,
estado_aseguramiento.`descripcion` aseguramiento,
naturaleza_evento.`descripcion` naturalezaEvento,
accidente.`descripcion_otro_evento` ,
accidente.`direccion_evento` ,
accidente.`fecha_evento`,
accidente.`hora_evento`,
departamento.`codigo` codigoDepartamentoEvento,
departamento.`nombre` departamenteEvento,
municipio.`codigo_dane` codigoMunicipio,
municipio.`nombre` minicipioEvento,
accidente.`zona`,
accidente.`descripcion` descripcionEvento,
accidente.`prestador_id`,
estado_aseguramiento.`descripcion` estadoAseguramiento,
accidente.`numero_rad_siras`,
accidente.`vehiculo_id`
FROM 
`accidente`
INNER JOIN `estado_aseguramiento` ON accidente.`estado_aseguramiento_id`=estado_aseguramiento.`id`
INNER JOIN  `naturaleza_evento` ON accidente.`naturaleza_evento_id`=naturaleza_evento.`id`
INNER JOIN   `municipio` ON accidente.`municipio_evento_id`=municipio.`id`
INNER JOIN  `departamento` ON municipio.`departamento_id`=departamento.`id`
WHERE accidente.`id`=11
), setPrestador AS (

SELECT
  prestador_salud.`id`,
  `codigo_habilitacion`,
  `razon_social`,
  `nit`,
  `telefono`,
   municipio.`nombre` municipio ,
   departamento.`nombre` departamento ,
  `direccion`,
  setAccidente.idAccidente idAccidentePrestador
FROM
  `furips`.`prestador_salud`
  INNER JOIN `municipio` ON prestador_salud.`municipio_id`=municipio.`id`
  INNER JOIN  `departamento` ON departamento.`id`=municipio.`departamento_id`
  INNER JOIN setAccidente ON prestador_salud.`id`=setAccidente.prestador_id
 
), `accidente_victima` AS (
 SELECT 
 accidente_victima.`accidente_id` ,
  setAccidente.idAccidente idAccidenteVictima,
  persona.`primer_apellido` primerApellidoVictima,
  persona.`segundo_apellido` segundoApellidoVictima ,
  persona.`primer_nombre` primerNombreVictima,
  persona.`segundo_nombre` segundoNombreVictima ,
  tipo_identificacion.`codigo` TipoidentificacionVictima,
  persona.`numero_identificacion` identificacionVictima,
  sexo.`codigo` sexoVictima,
  persona.`direccion` direccionVictima,
  departamento.`nombre` departamentoVictima,
  departamento.`codigo` codDepartamentoVictima,
  municipio.`nombre` municipioVictima,
  municipio.`codigo_dane` codMunicipioVictima,
  persona.`telefono` telefonoVictima,
  CASE accidente_victima.`condicion_codigo`
        WHEN 1 THEN 'conductor'
        WHEN 2 THEN 'peatón'
        WHEN 3 THEN 'ocupante'
        WHEN 4 THEN 'ciclista'
        ELSE 'otro' 
    END AS condicion_victima
 FROM 
 `accidente_victima`
 INNER JOIN  setAccidente ON accidente_victima.`accidente_id`=setAccidente.idAccidente
 INNER JOIN `persona` ON accidente_victima.`persona_id`=persona.`id`
 INNER JOIN  `tipo_identificacion` ON persona.`tipo_identificacion_id`=tipo_identificacion.`id`
 INNER JOIN `sexo` ON persona.`sexo_id`=sexo.`id`
 INNER JOIN  `municipio`ON persona.`municipio_residencia_id`= `municipio`.`id`
 INNER JOIN  `departamento` ON municipio.`departamento_id`=departamento.`id`
), setVehiculo AS (

SELECT 
setAccidente.estadoAseguramiento,
vehiculo.`marca`,
vehiculo.`placa`,
tipo_vehiculo.`descripcion`,
vehiculo.`aseguradora_codigo`,
vehiculo.`numero_poliza`,
setAccidente.numero_rad_siras,
vehiculo.`vigencia_inicio`,
vehiculo.`vigencia_fin`,
setAccidente.idAccidente idAccidenteVehiculo
FROM `vehiculo`
INNER JOIN setAccidente ON vehiculo.`id`=setAccidente.vehiculo_id
INNER JOIN `tipo_vehiculo` ON vehiculo.`tipo_vehiculo_id`=tipo_vehiculo.`id`

)

, setPropietario AS (

SELECT
setAccidente.idAccidente idAccidentePropietario,
  persona.`primer_apellido` primerApellidoPropietario,
  persona.`segundo_apellido` segundoApellidoPropietario ,
  persona.`primer_nombre` primerNombrePropietario,
  persona.`segundo_nombre` segundoNombrePropietario ,
  tipo_identificacion.`codigo` TipoidentificacionPropietario,
  persona.`numero_identificacion` identificacionPropietario,
  persona.`direccion` direccionPropietario,
  departamento.`nombre` departamentoPropietario,
  departamento.`codigo` codDepartamentoPropietario,
  municipio.`nombre` municipioPropietario,
  municipio.`codigo_dane` codMunicipioPropietario,
  persona.`telefono` telefonoPropietario
 
FROM `accidente_propietario`
INNER JOIN  setAccidente ON accidente_propietario.`accidente_id`=setAccidente.idAccidente
INNER JOIN `persona` ON accidente_propietario.`persona_id`=persona.`id`
INNER JOIN  `tipo_identificacion` ON persona.`tipo_identificacion_id`=tipo_identificacion.`id`
INNER JOIN  `municipio`ON persona.`municipio_residencia_id`= `municipio`.`id`
INNER JOIN  `departamento` ON municipio.`departamento_id`=departamento.`id`


), setConductor AS (

SELECT
setAccidente.idAccidente idAccidenteConductor,
  persona.`primer_apellido` primerApellidoConductor,
  persona.`segundo_apellido` segundoApellidoConductor ,
  persona.`primer_nombre` primerNombreConductoro,
  persona.`segundo_nombre` segundoNombreConductor ,
  tipo_identificacion.`codigo` TipoidentificacionConductor,
  persona.`numero_identificacion` identificacionConductor,
  persona.`direccion` direccionConductor,
  departamento.`nombre` departamentoConductor,
  departamento.`codigo` codDepartamentoConductor,
  municipio.`nombre` municipioConductor,
  municipio.`codigo_dane` codMunicipioConductor,
  persona.`telefono` telefonoConductor
 
FROM `accidente_conductor`
INNER JOIN  setAccidente ON accidente_conductor.`accidente_id`=setAccidente.idAccidente
INNER JOIN `persona` ON accidente_conductor.`persona_id`=persona.`id`
INNER JOIN  `tipo_identificacion` ON persona.`tipo_identificacion_id`=tipo_identificacion.`id`
INNER JOIN  `municipio`ON persona.`municipio_residencia_id`= `municipio`.`id`
INNER JOIN  `departamento` ON municipio.`departamento_id`=departamento.`id`
) , setRemision AS (

SELECT 
  CASE accidente_remision.`tipo_referencia`
        WHEN 1 THEN 'remision'
        WHEN 2 THEN 'orden Servicio'
        ELSE 'otro' 
    END AS tipo_referencia,
    accidente_remision.`fecha_remision`,
    accidente_remision.`hora_salida`,
    prestador_salud.`razon_social`,
    prestador_salud.`codigo_habilitacion`,
    persona.`primer_apellido`,
    persona.`segundo_apellido`,
    persona.`primer_nombre`,
    persona.`segundo_nombre`,
    persona_config.`especialidad` cargo,
    accidente_remision.`fecha_aceptacion`,
    accidente_remision.`hora_aceptacion`,
    accidente_remision.`ipsRecibe`,
    accidente_remision.`codigo_hab_recibe`,
    accidente_remision.`profesional_recibe`,
    accidente_remision.`cargo_Recibe`,
    accidente_remision.`placa_ambulancia`,
    setAccidente.idAccidente idAccidenteRemision
	
FROM `accidente_remision`
INNER JOIN setAccidente ON accidente_remision.`accidente_id`=setAccidente.idAccidente
INNER JOIN  persona ON accidente_remision.`persona_remite_id`=persona.`id`
INNER JOIN  `persona_config` ON persona.`id`=persona_config.`persona_id`
INNER JOIN  `prestador_salud` ON accidente_remision.prestadorId=prestador_salud.`id`

), setMedico AS (

SELECT 
    persona.`primer_apellido` primer_apellido_medico ,
    persona.`segundo_apellido` segundo_apellido_medico,
    persona.`primer_nombre` primer_nombre_medico ,
    persona.`segundo_nombre` segundo_nombre_medico,
    tipo_identificacion.`codigo` Tipoidentificacion_medico,
    persona.`numero_identificacion` numero_identificacion_medico,
    tipo_identificacion.`codigo` tipo_identificacion_medico,
    persona_config.`registro_medico`,
    setAccidente.idAccidente idAccidenteMedico
FROM `accidente_medico_tratante`
INNER JOIN setAccidente ON accidente_medico_tratante.`accidente_id`=setAccidente.idAccidente
INNER JOIN  persona ON accidente_medico_tratante.`persona_id`=persona.`id`
INNER JOIN  `persona_config` ON persona.`id`=persona_config.`persona_id`
INNER JOIN  `tipo_identificacion` ON persona.`tipo_identificacion_id`=tipo_identificacion.`id`

), totales AS (

SELECT
    accidente_detalle.`accidente_id`,
    SUM(
        CASE
            WHEN accidente_detalle.`tipo_servicio_id` = 4
            THEN accidente_detalle.`valor_unitario`
            ELSE 0
        END
    ) AS gastosMovilizacion,
    SUM(
        CASE
            WHEN accidente_detalle.`tipo_servicio_id` != 4
            THEN accidente_detalle.`valor_unitario`
            ELSE 0
        END
    ) AS gastosQx,
    accidente_detalle.`accidente_id` idAccidenteTotal
FROM
    `accidente_detalle`
    INNER JOIN setAccidente ON accidente_detalle.`accidente_id` = setAccidente.idAccidente
GROUP BY
    accidente_detalle.`accidente_id`


)

SELECT setAccidente.*, setPrestador.*, accidente_victima.*, setVehiculo.* , setPropietario.*, setConductor.*, setRemision.* , setMedico.*,totales.*
FROM setAccidente
LEFT  JOIN setPrestador ON setAccidente.idAccidente=setPrestador.idAccidentePrestador
LEFT  JOIN accidente_victima ON setAccidente.idAccidente=accidente_victima.idAccidenteVictima
LEFT  JOIN setVehiculo ON setAccidente.idAccidente=setVehiculo.idAccidenteVehiculo
LEFT  JOIN setPropietario ON setAccidente.idAccidente=setPropietario.idAccidentePropietario
LEFT  JOIN setConductor ON setAccidente.idAccidente=setConductor.idAccidenteConductor
LEFT  JOIN setRemision  ON setAccidente.idAccidente=setRemision.idAccidenteRemision
LEFT  JOIN setMedico  ON setAccidente.idAccidente=setMedico.idAccidenteMedico
LEFT  JOIN  totales ON setAccidente.idAccidente=totales.idAccidenteTotal 