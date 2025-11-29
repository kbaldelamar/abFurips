/*
SQLyog Ultimate v12.4.3 (64 bit)
MySQL - 11.4.2-MariaDB-ubu2404 : Database - furips
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`furips` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;

/*Table structure for table `accidente` */

DROP TABLE IF EXISTS `accidente`;

CREATE TABLE `accidente` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK accidente/evento',
  `prestador_id` bigint(20) unsigned NOT NULL COMMENT 'FK prestador que radica',
  `numero_consecutivo` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL COMMENT 'Consecutivo único por prestador',
  `numero_factura` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL COMMENT 'Número de factura',
  `numero_rad_siras` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL COMMENT 'Radicado SIRAS',
  `naturaleza_evento_id` tinyint(3) unsigned NOT NULL COMMENT 'FK naturaleza del evento',
  `descripcion_otro_evento` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT 'Descripción si la naturaleza es "otro"',
  `fecha_evento` date NOT NULL COMMENT 'Fecha del evento',
  `hora_evento` time NOT NULL COMMENT 'Hora del evento',
  `municipio_evento_id` int(10) unsigned NOT NULL COMMENT 'FK municipio del evento',
  `direccion_evento` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL COMMENT 'Dirección de ocurrencia',
  `zona` enum('U','R') CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT 'Zona urbana/rural',
  `vehiculo_id` bigint(20) unsigned DEFAULT NULL COMMENT 'FK vehículo involucrado',
  `estado_aseguramiento_id` tinyint(3) unsigned NOT NULL COMMENT 'FK estado del aseguramiento',
  `descripcion` text DEFAULT NULL COMMENT 'descripcion breve del evento',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_accidente_prestador_consec` (`prestador_id`,`numero_consecutivo`),
  KEY `fk_accidente_naturaleza` (`naturaleza_evento_id`),
  KEY `fk_accidente_municipio` (`municipio_evento_id`),
  KEY `fk_accidente_vehiculo` (`vehiculo_id`),
  KEY `fk_accidente_estado` (`estado_aseguramiento_id`),
  CONSTRAINT `fk_accidente_estado` FOREIGN KEY (`estado_aseguramiento_id`) REFERENCES `estado_aseguramiento` (`id`),
  CONSTRAINT `fk_accidente_municipio` FOREIGN KEY (`municipio_evento_id`) REFERENCES `municipio` (`id`),
  CONSTRAINT `fk_accidente_naturaleza` FOREIGN KEY (`naturaleza_evento_id`) REFERENCES `naturaleza_evento` (`id`),
  CONSTRAINT `fk_accidente_prestador` FOREIGN KEY (`prestador_id`) REFERENCES `prestador_salud` (`id`),
  CONSTRAINT `fk_accidente_vehiculo` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

/*Table structure for table `accidente_conductor` */

DROP TABLE IF EXISTS `accidente_conductor`;

CREATE TABLE `accidente_conductor` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK conductor vinculado',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `persona_id` bigint(20) unsigned NOT NULL COMMENT 'FK persona conductor',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  KEY `fk_accidente_conductor_acc` (`accidente_id`),
  KEY `fk_accidente_conductor_persona` (`persona_id`),
  CONSTRAINT `fk_accidente_conductor_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_conductor_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `accidente_detalle` */

DROP TABLE IF EXISTS `accidente_detalle`;

CREATE TABLE `accidente_detalle` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK detalle FURIPS2',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `tipo_servicio_id` tinyint(3) unsigned NOT NULL COMMENT 'FK tipo de servicio (1..8)',
  `procedimiento_id` bigint(20) unsigned DEFAULT NULL COMMENT 'FK procedimiento/catálogo',
  `codigo_servicio` varchar(15) DEFAULT NULL COMMENT 'Código del servicio (CUM, SOAT, etc.)',
  `descripcion` varchar(200) DEFAULT NULL COMMENT 'Descripción del ítem facturado',
  `cantidad` bigint(20) unsigned NOT NULL DEFAULT 0 COMMENT 'Cantidad del servicio',
  `valor_unitario` bigint(20) unsigned NOT NULL DEFAULT 0 COMMENT 'Valor unitario facturado',
  `valor_facturado` bigint(20) unsigned NOT NULL DEFAULT 0 COMMENT 'Valor total facturado',
  `valor_reclamado` bigint(20) unsigned NOT NULL DEFAULT 0 COMMENT 'Valor total reclamado',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  KEY `fk_accidente_detalle_acc` (`accidente_id`),
  KEY `fk_accidente_detalle_tipo` (`tipo_servicio_id`),
  KEY `fk_accidente_detalle_procedimiento` (`procedimiento_id`),
  CONSTRAINT `fk_accidente_detalle_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_detalle_procedimiento` FOREIGN KEY (`procedimiento_id`) REFERENCES `procedimiento` (`id`),
  CONSTRAINT `fk_accidente_detalle_tipo` FOREIGN KEY (`tipo_servicio_id`) REFERENCES `tipo_servicio` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `accidente_medico_tratante` */

DROP TABLE IF EXISTS `accidente_medico_tratante`;

CREATE TABLE `accidente_medico_tratante` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK vínculo médico tratante',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `accidente_victima_id` bigint(20) unsigned NOT NULL COMMENT 'FK víctima atendida',
  `persona_id` bigint(20) unsigned NOT NULL COMMENT 'FK persona del médico tratante',
  `fecha_ingreso` date DEFAULT NULL COMMENT '80: fecha de ingreso a IPS',
  `fecha_egreso` date DEFAULT NULL COMMENT '82: fecha de egreso de IPS',
  `diagnostico_ingreso` char(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT '84: CIE10 principal ingreso',
  `diagnostico_ingreso_sec1` char(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT '85: CIE10 ingreso asociado 1',
  `diagnostico_ingreso_sec2` char(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT '86: CIE10 ingreso asociado 2',
  `diagnostico_egreso` char(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT '87: CIE10 principal egreso',
  `diagnostico_egreso_sec1` char(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT '88: CIE10 egreso asociado 1',
  `diagnostico_egreso_sec2` char(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT '89: CIE10 egreso asociado 2',
  `servicio_uci` tinyint(1) DEFAULT NULL COMMENT 'Uso de UCI: 0=no, 1=sí',
  `dias_uci` smallint(5) unsigned DEFAULT NULL COMMENT 'Días en UCI reclamados',
  `estado` enum('activo','inactivo') CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci NOT NULL DEFAULT 'activo' COMMENT 'Estatus lógico del vínculo',
  `creado_en` timestamp NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación',
  `actualizado_en` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Fecha de última actualización',
  `hora_ingreso` time DEFAULT NULL COMMENT '81: hora de ingreso a IPS',
  `hora_egreso` time DEFAULT NULL COMMENT '83: hora de egreso de IPS',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_medico_victima` (`accidente_victima_id`),
  KEY `fk_am_trat_accidente` (`accidente_id`),
  KEY `fk_am_trat_persona` (`persona_id`),
  CONSTRAINT `fk_am_trat_accidente` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_am_trat_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`),
  CONSTRAINT `fk_am_trat_victima` FOREIGN KEY (`accidente_victima_id`) REFERENCES `accidente_victima` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

/*Table structure for table `accidente_propietario` */

DROP TABLE IF EXISTS `accidente_propietario`;

CREATE TABLE `accidente_propietario` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK propietario vinculado',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `persona_id` bigint(20) unsigned NOT NULL COMMENT 'FK persona propietaria',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  KEY `fk_accidente_propietario_acc` (`accidente_id`),
  KEY `fk_accidente_propietario_persona` (`persona_id`),
  CONSTRAINT `fk_accidente_propietario_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_propietario_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `accidente_remision` */

DROP TABLE IF EXISTS `accidente_remision`;

CREATE TABLE `accidente_remision` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente (padre)',
  `tipo_referencia` tinyint(4) NOT NULL COMMENT '1 = Remite paciente, 2 = Orden de servicio, 3 = Recibe paciente',
  `fecha_remision` date DEFAULT NULL,
  `hora_salida` time DEFAULT NULL,
  `codigo_hab_remitente` varchar(12) DEFAULT NULL,
  `profesional_remite` varchar(60) DEFAULT NULL,
  `cargo_remite` varchar(30) DEFAULT NULL,
  `fecha_aceptacion` date DEFAULT NULL,
  `hora_aceptacion` time DEFAULT NULL,
  `codigo_hab_recibe` varchar(12) DEFAULT NULL,
  `profesional_recibe` varchar(60) DEFAULT NULL,
  `placa_ambulancia` varchar(12) DEFAULT NULL,
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo',
  `persona_remite_id` bigint(20) unsigned DEFAULT NULL,
  `persona_recibe_id` bigint(20) unsigned DEFAULT NULL,
  `creado_en` timestamp NULL DEFAULT current_timestamp(),
  `actualizado_en` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_acc_rem_accidente` (`accidente_id`),
  KEY `fk_acc_rem_persona_remite` (`persona_remite_id`),
  KEY `fk_acc_rem_persona_recibe` (`persona_recibe_id`),
  CONSTRAINT `fk_acc_rem_accidente` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_acc_rem_persona_recibe` FOREIGN KEY (`persona_recibe_id`) REFERENCES `persona` (`id`),
  CONSTRAINT `fk_acc_rem_persona_remite` FOREIGN KEY (`persona_remite_id`) REFERENCES `persona` (`id`),
  CONSTRAINT `chk_acc_rem_tipo` CHECK (`tipo_referencia` in (1,2,3))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

/*Table structure for table `accidente_totales` */

DROP TABLE IF EXISTS `accidente_totales`;

CREATE TABLE `accidente_totales` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK totales FURIPS1',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `total_facturado_gmq` bigint(20) unsigned NOT NULL COMMENT 'Campo 97: total facturado gastos médico-quirúrgicos',
  `total_reclamado_gmq` bigint(20) unsigned NOT NULL COMMENT 'Campo 98: total reclamado gastos médico-quirúrgicos',
  `total_facturado_transporte` bigint(20) unsigned NOT NULL COMMENT 'Campo 99: total facturado transporte primario',
  `total_reclamado_transporte` bigint(20) unsigned NOT NULL COMMENT 'Campo 100: total reclamado transporte primario',
  `manifestacion_servicios` tinyint(1) NOT NULL COMMENT 'Campo 101: 0/1 servicios habilitados',
  `descripcion_evento` varchar(1000) NOT NULL COMMENT 'Campo 102: descripción breve del evento',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_totales_accidente` (`accidente_id`),
  CONSTRAINT `fk_totales_accidente` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `accidente_victima` */

DROP TABLE IF EXISTS `accidente_victima`;

CREATE TABLE `accidente_victima` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK víctima del accidente',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `persona_id` bigint(20) unsigned NOT NULL COMMENT 'FK persona víctima',
  `condicion_codigo` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL COMMENT '1 conductor, 2 peatón, 3 ocupante, 4 ciclista',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  KEY `fk_accidente_victima_acc` (`accidente_id`),
  KEY `fk_accidente_victima_persona` (`persona_id`),
  CONSTRAINT `fk_accidente_victima_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_victima_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

/*Table structure for table `departamento` */

DROP TABLE IF EXISTS `departamento`;

CREATE TABLE `departamento` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK departamento',
  `pais_id` smallint(5) unsigned NOT NULL COMMENT 'FK a pais.id',
  `codigo` char(3) NOT NULL COMMENT 'Código interno/DANE depto',
  `nombre` varchar(60) NOT NULL COMMENT 'Nombre del departamento',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `pais_id` (`pais_id`,`codigo`),
  CONSTRAINT `fk_departamento_pais` FOREIGN KEY (`pais_id`) REFERENCES `pais` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `estado_aseguramiento` */

DROP TABLE IF EXISTS `estado_aseguramiento`;

CREATE TABLE `estado_aseguramiento` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK estado de aseguramiento',
  `codigo` char(1) NOT NULL COMMENT '1,2,3,4,6,7,8 según circular',
  `descripcion` varchar(60) NOT NULL COMMENT 'Descripción del estado de aseguramiento',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `municipio` */

DROP TABLE IF EXISTS `municipio`;

CREATE TABLE `municipio` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK municipio',
  `departamento_id` int(10) unsigned NOT NULL COMMENT 'FK a departamento.id',
  `codigo_dane` char(5) NOT NULL COMMENT 'Código DANE municipio',
  `codigo_postal` char(6) DEFAULT NULL COMMENT 'Código postal',
  `nombre` varchar(80) NOT NULL COMMENT 'Nombre del municipio',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `departamento_id` (`departamento_id`,`codigo_dane`),
  CONSTRAINT `fk_municipio_departamento` FOREIGN KEY (`departamento_id`) REFERENCES `departamento` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `naturaleza_evento` */

DROP TABLE IF EXISTS `naturaleza_evento`;

CREATE TABLE `naturaleza_evento` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK naturaleza del evento',
  `codigo` char(2) NOT NULL COMMENT '01..27 según circular',
  `descripcion` varchar(60) NOT NULL COMMENT 'Descripción de la naturaleza',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `pais` */

DROP TABLE IF EXISTS `pais`;

CREATE TABLE `pais` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK país',
  `codigo` char(3) NOT NULL COMMENT 'Código ISO u homólogo',
  `nombre` varchar(60) NOT NULL COMMENT 'Nombre del país',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `persona` */

DROP TABLE IF EXISTS `persona`;

CREATE TABLE `persona` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK persona',
  `tipo_identificacion_id` tinyint(3) unsigned NOT NULL COMMENT 'FK tipo_identificacion',
  `numero_identificacion` varchar(20) NOT NULL COMMENT 'Número de documento',
  `primer_nombre` varchar(30) NOT NULL COMMENT 'Primer nombre',
  `segundo_nombre` varchar(30) DEFAULT NULL COMMENT 'Segundo nombre',
  `primer_apellido` varchar(30) NOT NULL COMMENT 'Primer apellido',
  `segundo_apellido` varchar(30) DEFAULT NULL COMMENT 'Segundo apellido',
  `sexo_id` tinyint(3) unsigned NOT NULL COMMENT 'FK sexo',
  `fecha_nacimiento` date NOT NULL COMMENT 'Fecha de nacimiento',
  `fecha_fallecimiento` date DEFAULT NULL COMMENT 'Fecha de fallecimiento (si aplica)',
  `direccion` varchar(200) NOT NULL COMMENT 'Dirección de residencia',
  `telefono` varchar(15) NOT NULL COMMENT 'Teléfono de contacto',
  `municipio_residencia_id` int(10) unsigned NOT NULL COMMENT 'FK municipio de residencia',
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Fecha de creación del registro',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_persona_doc` (`tipo_identificacion_id`,`numero_identificacion`),
  KEY `fk_persona_sexo` (`sexo_id`),
  KEY `fk_persona_municipio` (`municipio_residencia_id`),
  CONSTRAINT `fk_persona_municipio` FOREIGN KEY (`municipio_residencia_id`) REFERENCES `municipio` (`id`),
  CONSTRAINT `fk_persona_sexo` FOREIGN KEY (`sexo_id`) REFERENCES `sexo` (`id`),
  CONSTRAINT `fk_persona_tipo` FOREIGN KEY (`tipo_identificacion_id`) REFERENCES `tipo_identificacion` (`id`),
  CONSTRAINT `chk_persona_fallecimiento` CHECK (`fecha_fallecimiento` is null or `fecha_fallecimiento` >= `fecha_nacimiento`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `persona_config` */

DROP TABLE IF EXISTS `persona_config`;

CREATE TABLE `persona_config` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `persona_id` bigint(20) unsigned NOT NULL,
  `es_medico` tinyint(1) NOT NULL DEFAULT 0,
  `registro_medico` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL,
  `especialidad` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci DEFAULT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1,
  `creado_en` timestamp NULL DEFAULT current_timestamp(),
  `actualizado_en` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_persona_config` (`persona_id`),
  CONSTRAINT `fk_persona_config_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

/*Table structure for table `prestador_salud` */

DROP TABLE IF EXISTS `prestador_salud`;

CREATE TABLE `prestador_salud` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK prestador IPS',
  `codigo_habilitacion` char(12) NOT NULL COMMENT 'Código de habilitación IPS',
  `razon_social` varchar(120) NOT NULL COMMENT 'Razón social IPS',
  `nit` varchar(15) DEFAULT NULL COMMENT 'NIT de la IPS',
  `telefono` varchar(15) DEFAULT NULL COMMENT 'Contacto telefónico',
  `municipio_id` int(10) unsigned DEFAULT NULL COMMENT 'FK municipio de la IPS',
  `direccion` varchar(200) DEFAULT NULL COMMENT 'Dirección de la IPS',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_habilitacion` (`codigo_habilitacion`),
  KEY `fk_prestador_municipio` (`municipio_id`),
  CONSTRAINT `fk_prestador_municipio` FOREIGN KEY (`municipio_id`) REFERENCES `municipio` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `procedimiento` */

DROP TABLE IF EXISTS `procedimiento`;

CREATE TABLE `procedimiento` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK procedimiento/catálogo',
  `codigo` varchar(15) NOT NULL COMMENT 'Código interno del procedimiento',
  `descripcion` varchar(200) DEFAULT NULL COMMENT 'Descripción del procedimiento',
  `codigo_soat` varchar(10) DEFAULT NULL COMMENT 'Código SOAT (si aplica)',
  `valor` bigint(20) unsigned NOT NULL COMMENT 'Valor base del procedimiento',
  `estado` enum('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO' COMMENT 'Estado del procedimiento',
  `es_traslado_primario` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Marca si es traslado primario',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_procedimiento_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `propietario_historial` */

DROP TABLE IF EXISTS `propietario_historial`;

CREATE TABLE `propietario_historial` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `accidente_id` int(11) NOT NULL COMMENT 'ID del accidente relacionado',
  `propietario_id_anterior` int(11) DEFAULT NULL COMMENT 'ID del propietario anulado (si aplica)',
  `propietario_id_nuevo` int(11) DEFAULT NULL COMMENT 'ID del nuevo propietario creado (si aplica)',
  `persona_id_anterior` int(11) DEFAULT NULL COMMENT 'ID de la persona del propietario anulado',
  `persona_id_nueva` int(11) DEFAULT NULL COMMENT 'ID de la persona del nuevo propietario',
  `accion` varchar(50) NOT NULL COMMENT 'ANULAR, CREAR, ACTUALIZAR',
  `documento_anterior` varchar(20) DEFAULT NULL COMMENT 'Documento del propietario anulado',
  `documento_nuevo` varchar(20) DEFAULT NULL COMMENT 'Documento del nuevo propietario',
  `motivo` varchar(500) DEFAULT NULL COMMENT 'Motivo del cambio',
  `usuario` varchar(100) DEFAULT NULL COMMENT 'Usuario que realizó el cambio',
  `fecha_cambio` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_accidente` (`accidente_id`),
  KEY `idx_propietario_anterior` (`propietario_id_anterior`),
  KEY `idx_propietario_nuevo` (`propietario_id_nuevo`),
  KEY `idx_fecha` (`fecha_cambio`),
  KEY `idx_ph_documento_anterior` (`documento_anterior`),
  KEY `idx_ph_documento_nuevo` (`documento_nuevo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Auditoría de cambios en propietarios asociados a accidentes';

/*Table structure for table `sexo` */

DROP TABLE IF EXISTS `sexo`;

CREATE TABLE `sexo` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK sexo',
  `codigo` char(1) NOT NULL COMMENT 'F, M, O',
  `descripcion` varchar(15) NOT NULL COMMENT 'Descripción del sexo',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `tipo_identificacion` */

DROP TABLE IF EXISTS `tipo_identificacion`;

CREATE TABLE `tipo_identificacion` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK tipo de identificación',
  `codigo` char(2) NOT NULL COMMENT 'Código (CC, CE, etc.)',
  `descripcion` varchar(50) NOT NULL COMMENT 'Descripción del tipo de documento',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `tipo_servicio` */

DROP TABLE IF EXISTS `tipo_servicio`;

CREATE TABLE `tipo_servicio` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK tipo de servicio FURIPS2',
  `codigo` char(1) NOT NULL COMMENT '1..8 tipos de servicio',
  `descripcion` varchar(40) NOT NULL COMMENT 'Descripción del tipo de servicio',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `tipo_vehiculo` */

DROP TABLE IF EXISTS `tipo_vehiculo`;

CREATE TABLE `tipo_vehiculo` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK tipo de vehículo',
  `codigo` char(2) NOT NULL COMMENT 'Código de tipo de vehículo',
  `descripcion` varchar(40) NOT NULL COMMENT 'Descripción del tipo de vehículo',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `vehiculo` */

DROP TABLE IF EXISTS `vehiculo`;

CREATE TABLE `vehiculo` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK vehículo',
  `placa` varchar(10) DEFAULT NULL COMMENT 'Placa del vehículo',
  `marca` varchar(30) DEFAULT NULL COMMENT 'Marca del vehículo',
  `tipo_vehiculo_id` tinyint(3) unsigned DEFAULT NULL COMMENT 'FK tipo de vehículo',
  `aseguradora_codigo` char(6) DEFAULT NULL COMMENT 'Código de aseguradora (AT)',
  `numero_poliza` varchar(20) DEFAULT NULL COMMENT 'Número de póliza SOAT',
  `vigencia_inicio` date DEFAULT NULL COMMENT 'Inicio vigencia póliza',
  `vigencia_fin` date DEFAULT NULL COMMENT 'Fin vigencia póliza',
  `estado_aseguramiento_id` tinyint(3) unsigned NOT NULL COMMENT 'FK estado de aseguramiento',
  `propietario_id` bigint(20) unsigned DEFAULT NULL COMMENT 'FK propietario (persona)',
  `estado` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 activo, 0 inactivo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `placa` (`placa`),
  KEY `fk_vehiculo_tipo` (`tipo_vehiculo_id`),
  KEY `fk_vehiculo_estado` (`estado_aseguramiento_id`),
  KEY `fk_vehiculo_propietario` (`propietario_id`),
  CONSTRAINT `fk_vehiculo_estado` FOREIGN KEY (`estado_aseguramiento_id`) REFERENCES `estado_aseguramiento` (`id`),
  CONSTRAINT `fk_vehiculo_propietario` FOREIGN KEY (`propietario_id`) REFERENCES `persona` (`id`),
  CONSTRAINT `fk_vehiculo_tipo` FOREIGN KEY (`tipo_vehiculo_id`) REFERENCES `tipo_vehiculo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Table structure for table `vehiculo_historial` */

DROP TABLE IF EXISTS `vehiculo_historial`;

CREATE TABLE `vehiculo_historial` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `accidente_id` int(11) NOT NULL COMMENT 'ID del accidente relacionado',
  `vehiculo_id_anterior` int(11) DEFAULT NULL COMMENT 'ID del vehículo anulado (si aplica)',
  `vehiculo_id_nuevo` int(11) DEFAULT NULL COMMENT 'ID del nuevo vehículo creado (si aplica)',
  `accion` varchar(50) NOT NULL COMMENT 'ANULAR, CREAR, ACTUALIZAR',
  `placa_anterior` varchar(10) DEFAULT NULL COMMENT 'Placa del vehículo anulado',
  `placa_nueva` varchar(10) DEFAULT NULL COMMENT 'Placa del nuevo vehículo',
  `motivo` varchar(500) DEFAULT NULL COMMENT 'Motivo del cambio',
  `usuario` varchar(100) DEFAULT NULL COMMENT 'Usuario que realizó el cambio',
  `fecha_cambio` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_accidente` (`accidente_id`),
  KEY `idx_vehiculo_anterior` (`vehiculo_id_anterior`),
  KEY `idx_vehiculo_nuevo` (`vehiculo_id_nuevo`),
  KEY `idx_fecha` (`fecha_cambio`),
  KEY `idx_vh_placa_anterior` (`placa_anterior`),
  KEY `idx_vh_placa_nueva` (`placa_nueva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Auditoría de cambios en vehículos asociados a accidentes';

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
