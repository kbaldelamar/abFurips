"""Servicio para generar PDFs FURIPS desde datos de accidente.

Se corrigió la estructura y se agregó soporte explícito para la CTE
que proviene del usuario (modo `furips_cte`).
"""

from pathlib import Path
from typing import Dict, Any, Optional
import traceback
import datetime

from app.config.settings import get_settings
from app.config.db import get_db_session
from app.infra.pdf.stamper import PDFStamper
from app.data.repositories.accidente_repo import AccidenteRepository
from sqlalchemy import text


class PrintService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.stamper = PDFStamper()

    def generar_pdf_accidente(self, accidente_id: int, tipo: str = "furips1") -> Path:
        """Genera el PDF para un accidente y retorna la ruta al archivo.

        - `furips1` o cualquier otro valor distinto de 'furips2' usarán la
          plantilla FURIPS1 (mapeo por objetos).
        - `furips2` usará la plantilla FURIPS2.
        - `furips_cte` ejecuta la CTE exacta provista y usa FURIPS2.
        """
        with get_db_session() as session:
            output_dir = self.settings.get_output_dir()
            output_path = output_dir / f"furips_{accidente_id}_{tipo}.pdf"

            if tipo == "furips_cte":
                datos = self._get_datos_from_cte(session, accidente_id)
                if datos is None:
                    raise ValueError(f"No hay datos para accidente_id={accidente_id}")

                # Preferir el id que vino de la CTE cuando esté disponible
                cte_id = datos.get("idAccidente") or datos.get("idAccidenteTotal") or accidente_id
                # Usar el id real para el nombre del archivo
                output_path = output_dir / f"furips_{cte_id}_{tipo}.pdf"

                # Logear el id tomado de la consulta para depuración
                print(f"[PrintService] idAccidente desde CTE: {cte_id}")

                template = self.settings.get_pdf_template_path("furips2")
                print(f"[PrintService] plantilla: {template}")
                print(f"[PrintService] output_path: {output_path}")
                if not Path(template).exists():
                    # Intentar crear una plantilla mínima de prueba automáticamente
                    try:
                        Path(template).parent.mkdir(parents=True, exist_ok=True)
                        print(f"[PrintService] Plantilla no encontrada, creando plantilla de prueba en {template}")
                        try:
                            import fitz
                            doc = fitz.open()
                            doc.new_page()
                            doc.save(str(template))
                            doc.close()
                            print(f"[PrintService] Plantilla de prueba creada: {template}")
                        except Exception as e:
                            print("[PrintService] No se pudo crear la plantilla automática:")
                            traceback.print_exc()
                            raise FileNotFoundError(f"No such file: '{template}' - could not create placeholder (see console)")
                    except Exception:
                        # Si no podemos crear la carpeta/archivo, informar al usuario
                        raise FileNotFoundError(f"No such file: '{template}'")

                # Si existe la imagen de encabezado, generar desde cero usando esa imagen.
                image_path = Path("imagenes") / "Encabezado_Furips.png"
                print("[PrintService] Llamando a estampar_furips_desde_cero (si existe la imagen)...")
                try:
                    if image_path.exists():
                        saved = self.stamper.estampar_furips_desde_cero(image_path, output_path, datos)
                    else:
                        # Si no hay imagen, usar el flujo anterior con plantilla (si existe)
                        saved = self.stamper.estampar_furips2(template, output_path, datos)
                except Exception:
                    print("[PrintService] Error durante el estampeo:")
                    traceback.print_exc()
                    raise
                print(f"[PrintService] PDF guardado en: {saved}")
                return Path(saved)

            repo = AccidenteRepository(session)
            accidente = repo.get_by_id(accidente_id)
            if accidente is None:
                raise ValueError(f"Accidente no encontrado: {accidente_id}")

            datos = self._map_accidente_to_datos(accidente)

            if tipo == "furips2":
                template = self.settings.get_pdf_template_path("furips2")
                self.stamper.estampar_furips2(template, output_path, datos)
            else:
                template = self.settings.get_pdf_template_path("furips1")
                self.stamper.estampar_furips1(template, output_path, datos)

            return output_path

    def _map_accidente_to_datos(self, accidente) -> Dict[str, Any]:
        """Mapea un objeto Accidente al dict que espera el stamper."""
        datos: Dict[str, Any] = {}
        datos["codigo_habilitacion"] = getattr(accidente.prestador, "codigo_habilitacion", "")
        datos["razon_social"] = getattr(accidente.prestador, "razon_social", "")
        datos["consecutivo"] = getattr(accidente, "numero_consecutivo", "")
        datos["factura"] = getattr(accidente, "numero_factura", "")
        datos["rad_siras"] = getattr(accidente, "numero_rad_siras", "")
        datos["fecha_evento"] = getattr(accidente, "fecha_evento", "")
        datos["hora_evento"] = getattr(accidente, "hora_evento", "")
        datos["municipio"] = getattr(accidente.municipio_evento, "nombre", "")
        datos["direccion"] = getattr(accidente, "direccion_evento", "")
        datos["placa"] = getattr(accidente.vehiculo, "placa", "")

        victimas = getattr(accidente, "victimas", []) or []
        if victimas:
            persona = getattr(victimas[0], "persona", None)
            if persona:
                datos["victima_nombre"] = f"{getattr(persona, 'primer_nombre', '')} {getattr(persona, 'primer_apellido', '')}".strip()
                datos["victima_documento"] = getattr(persona, "numero_identificacion", "")
            else:
                datos["victima_nombre"] = ""
                datos["victima_documento"] = ""
        else:
            datos["victima_nombre"] = ""
            datos["victima_documento"] = ""

        tot = getattr(accidente, "totales", None)
        if tot:
            datos["total_gmq_facturado"] = getattr(tot, "total_facturado_gmq", 0)
            datos["total_gmq_reclamado"] = getattr(tot, "total_reclamado_gmq", 0)
            datos["total_transporte_facturado"] = getattr(tot, "total_facturado_transporte", 0)
            datos["total_transporte_reclamado"] = getattr(tot, "total_reclamado_transporte", 0)
            datos["descripcion_evento"] = getattr(tot, "descripcion_evento", "")
        else:
            datos["total_gmq_facturado"] = 0
            datos["total_gmq_reclamado"] = 0
            datos["total_transporte_facturado"] = 0
            datos["total_transporte_reclamado"] = 0
            datos["descripcion_evento"] = ""

        detalles = []
        for d in getattr(accidente, "detalles", []) or []:
            detalles.append({
                "tipo_servicio": getattr(d, "tipo_servicio_id", ""),
                "codigo": getattr(d, "procedimiento_id", ""),
                "descripcion": getattr(d, "descripcion", ""),
                "cantidad": getattr(d, "cantidad", 0),
                "valor_unitario": getattr(d, "valor_unitario", 0),
                "valor_facturado": getattr(d, "valor_facturado", 0),
                "valor_reclamado": getattr(d, "valor_reclamado", 0),
            })

        datos["detalles"] = detalles
        # Valor usado por el stamper (encabezado)
        datos["prestador"] = datos.get("razon_social", "")

        return datos

    def _get_datos_from_cte(self, session, accidente_id: int) -> Optional[Dict[str, Any]]:
        """Ejecuta la CTE exacta provista por el usuario y mapea la primera fila.

        Retorna None si no hay resultados.
        """
        sql = text(r"""
            WITH setAccidente AS (

            SELECT
            accidente.`id` idAccidente,
            accidente.`numero_factura`,
            accidente.`numero_consecutivo`,
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
            WHERE accidente.`id` = :accidente_id
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
                departamento.codigo codDepartamentoPropietario,
                municipio.nombre municipioPropietario,
                municipio.codigo_dane codMunicipioPropietario,
                persona.telefono telefonoPropietario
                FROM accidente_propietario
                INNER JOIN setAccidente ON accidente_propietario.accidente_id = setAccidente.idAccidente
                INNER JOIN persona ON accidente_propietario.persona_id = persona.id
                INNER JOIN tipo_identificacion ON persona.tipo_identificacion_id = tipo_identificacion.id
                INNER JOIN municipio ON persona.municipio_residencia_id = municipio.id
                INNER JOIN departamento ON municipio.departamento_id = departamento.id
                ), setConductor as (
        select
        setAccidente.idAccidente idAccidenteConductor,
          persona.primer_apellido primerApellidoConductor,
          persona.segundo_apellido segundoApellidoConductor ,
          persona.primer_nombre primerNombreConductoro,
          persona.segundo_nombre segundoNombreConductor ,
          tipo_identificacion.codigo TipoidentificacionConductor,
          persona.numero_identificacion identificacionConductor,
          persona.direccion direccionConductor,
          departamento.nombre departamentoConductor,
          departamento.codigo codDepartamentoConductor,
          municipio.nombre municipioConductor,
          municipio.codigo_dane codMunicipioConductor,
          persona.telefono telefonoConductor
        from accidente_conductor
        inner join  setAccidente on accidente_conductor.accidente_id=setAccidente.idAccidente
        inner join persona on accidente_conductor.persona_id=persona.id
        inner join  tipo_identificacion on persona.tipo_identificacion_id=tipo_identificacion.id
        INNER JOIN municipio ON persona.municipio_residencia_id = municipio.id
        INNER JOIN departamento ON municipio.departamento_id = departamento.id
        ) , setRemision as (
        select 
          CASE accidente_remision.tipo_referencia
                WHEN 1 THEN 'remision'
                WHEN 2 THEN 'orden Servicio'
                ELSE 'otro' 
            END AS tipo_referencia,
            accidente_remision.fecha_remision,
            accidente_remision.hora_salida,
            prestador_salud.razon_social,
            prestador_salud.codigo_habilitacion,
            persona.primer_apellido,
            persona.segundo_apellido,
            persona.primer_nombre,
            persona.segundo_nombre,
            persona_config.especialidad cargo,
            accidente_remision.fecha_aceptacion,
            accidente_remision.hora_aceptacion,
            accidente_remision.ipsRecibe,
            accidente_remision.codigo_hab_recibe,
            accidente_remision.profesional_recibe,
            accidente_remision.cargo_Recibe,
            accidente_remision.placa_ambulancia,
            setAccidente.idAccidente idAccidenteRemision
        from accidente_remision
        inner join setAccidente on accidente_remision.accidente_id=setAccidente.idAccidente
        inner join  persona on accidente_remision.persona_remite_id=persona.id
        inner join  persona_config on persona.id=persona_config.persona_id
        inner join  prestador_salud on accidente_remision.prestadorId=prestador_salud.id
        ), setMedico as (
        select 
            persona.primer_apellido primer_apellido_medico ,
            persona.segundo_apellido segundo_apellido_medico,
            persona.primer_nombre primer_nombre_medico ,
            persona.segundo_nombre segundo_nombre_medico,
            tipo_identificacion.codigo Tipoidentificacion_medico,
            persona.numero_identificacion numero_identificacion_medico,
            tipo_identificacion.codigo tipo_identificacion_medico,
            persona_config.registro_medico,
            setAccidente.idAccidente idAccidenteMedico
        from accidente_medico_tratante
        INNER JOIN setAccidente ON accidente_medico_tratante.accidente_id=setAccidente.idAccidente
        inner join  persona on accidente_medico_tratante.persona_id=persona.id
        inner join  persona_config on persona.id=persona_config.persona_id
        inner join  tipo_identificacion on persona.tipo_identificacion_id=tipo_identificacion.id
        )
        , totales AS (

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
        select setAccidente.*, setPrestador.*, accidente_victima.*, setVehiculo.* , setPropietario.*, setConductor.*, setRemision.* , setMedico.*
        from setAccidente
        LEFT  join setPrestador on setAccidente.idAccidente=setPrestador.idAccidentePrestador
        LEFT  join accidente_victima on setAccidente.idAccidente=accidente_victima.idAccidenteVictima
        LEFT  join setVehiculo on setAccidente.idAccidente=setVehiculo.idAccidenteVehiculo
        LEFT  join setPropietario on setAccidente.idAccidente=setPropietario.idAccidentePropietario
        LEFT  join setConductor on setAccidente.idAccidente=setConductor.idAccidenteConductor
        left  join setRemision  on setAccidente.idAccidente=setRemision.idAccidenteRemision
        left  join setMedico  on setAccidente.idAccidente=setMedico.idAccidenteMedico
        left  join  totales on setAccidente.idAccidente=totales.idAccidenteTotal
                   
        """)

        # Debug: show SQL and params
        try:
            print("[PrintService] Ejecutando CTE SQL:")
            print(sql)
            print("[PrintService] Params:", {"accidente_id": accidente_id})
        except Exception:
            pass

        try:
            result = session.execute(sql, {"accidente_id": accidente_id})
        except Exception as e:
            print("[PrintService] Error ejecutando SQL:")
            traceback.print_exc()
            raise

        mapping = result.mappings().first()
        print("[PrintService] RowMapping first():", dict(mapping) if mapping is not None else None)
        if mapping is None:
            return None

        # Helper to format time-like values coming as timedelta
        def _fmt_time(tv):
            try:
                if isinstance(tv, datetime.timedelta):
                    secs = int(tv.total_seconds())
                    h = secs // 3600
                    m = (secs % 3600) // 60
                    s = secs % 60
                    return f"{h:02d}:{m:02d}:{s:02d}"
                return str(tv) if tv is not None else ""
            except Exception:
                return ""

        datos: Dict[str, Any] = {}
        get = lambda key: mapping.get(key) if mapping.get(key) is not None else ""

        datos["codigo_habilitacion"] = get("codigo_habilitacion")
        datos["razon_social"] = get("razon_social")
        datos["consecutivo"] = get("numero_rad_siras") or get("idAccidente")
        datos["factura"] = get("numero_factura")
        datos["numero_consecutivo"] = get("numero_consecutivo")
        datos["rad_siras"] = get("numero_rad_siras")
        fecha_evt = mapping.get("fecha_evento")
        datos["fecha_evento"] = fecha_evt.isoformat() if fecha_evt else ""
        datos["hora_evento"] = _fmt_time(mapping.get("hora_evento"))
        datos["municipio"] = get("minicipioEvento") or get("municipio") or get("municipioEvento")
        datos["direccion"] = get("direccion_evento") or get("direccion")
        datos["placa"] = get("placa")

        nombre_v = f"{get('primerNombreVictima')} {get('primerApellidoVictima')}".strip()
        datos["victima_nombre"] = nombre_v
        datos["victima_documento"] = get("identificacionVictima")

        gastos_movilizacion = mapping.get("gastosMovilizacion") or 0
        gastos_qx = mapping.get("gastosQx") or 0
        datos["total_transporte_facturado"] = gastos_movilizacion
        datos["total_transporte_reclamado"] = gastos_movilizacion
        datos["total_gmq_facturado"] = gastos_qx
        datos["total_gmq_reclamado"] = gastos_qx

        datos["descripcion_evento"] = get("descripcionEvento")
        datos["detalles"] = []

        # Remission / referencia
        datos["remision_tipo"] = get("tipo_referencia")
        rem_fecha = mapping.get("fecha_remision")
        datos["remision_fecha"] = rem_fecha.isoformat() if rem_fecha else ""
        datos["remision_hora_salida"] = _fmt_time(mapping.get("hora_salida"))
        datos["ips_recibe"] = get("ipsRecibe")
        datos["codigo_hab_recibe"] = get("codigo_hab_recibe")
        datos["profesional_recibe"] = get("profesional_recibe")
        datos["cargo_recibe"] = get("cargo_Recibe")
        datos["placa_ambulancia"] = get("placa_ambulancia")

        # Médico tratante
        datos["medico_nombre"] = f"{get('primer_nombre_medico')} {get('primer_apellido_medico')}".strip()
        datos["medico_registro"] = get("registro_medico")
        datos["medico_identificacion"] = get("numero_identificacion_medico")

        # Conductor
        datos["conductor_nombre"] = f"{get('primerNombreConductoro')} {get('primerApellidoConductor')}".strip()
        datos["conductor_documento"] = get("identificacionConductor")

        # Propietario
        datos["propietario_telefono"] = get("telefonoPropietario")
        datos["propietario_municipio"] = get("municipioPropietario")

        # Asegurar que el id del accidente esté presente en los datos
        datos["idAccidente"] = mapping.get("idAccidente") or mapping.get("idAccidenteTotal") or accidente_id

        # Debug: mostrar un resumen de datos esenciales antes de devolver
        try:
            resumen = {k: datos.get(k) for k in ("idAccidente", "codigo_habilitacion", "razon_social", "consecutivo", "placa")}
            print("[PrintService] Datos resumen:", resumen)
        except Exception:
            pass

        # Asegurar clave 'prestador' para el stamper (FURIPS2 espera esta clave)
        datos["prestador"] = datos.get("razon_social", "")

        return datos
