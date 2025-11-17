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
  `numero_consecutivo` varchar(12) NOT NULL COMMENT 'Consecutivo único por prestador',
  `numero_factura` varchar(20) NOT NULL COMMENT 'Número de factura',
  `numero_rad_siras` varchar(20) NOT NULL COMMENT 'Radicado SIRAS',
  `naturaleza_evento_id` tinyint(3) unsigned NOT NULL COMMENT 'FK naturaleza del evento',
  `descripcion_otro_evento` varchar(25) DEFAULT NULL COMMENT 'Descripción si la naturaleza es "otro"',
  `fecha_evento` date NOT NULL COMMENT 'Fecha del evento',
  `hora_evento` time NOT NULL COMMENT 'Hora del evento',
  `municipio_evento_id` int(10) unsigned NOT NULL COMMENT 'FK municipio del evento',
  `direccion_evento` varchar(200) NOT NULL COMMENT 'Dirección de ocurrencia',
  `zona` enum('U','R') DEFAULT NULL COMMENT 'Zona urbana/rural',
  `vehiculo_id` bigint(20) unsigned DEFAULT NULL COMMENT 'FK vehículo involucrado',
  `estado_aseguramiento_id` tinyint(3) unsigned NOT NULL COMMENT 'FK estado del aseguramiento',
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `accidente` */

insert  into `accidente`(`id`,`prestador_id`,`numero_consecutivo`,`numero_factura`,`numero_rad_siras`,`naturaleza_evento_id`,`descripcion_otro_evento`,`fecha_evento`,`hora_evento`,`municipio_evento_id`,`direccion_evento`,`zona`,`vehiculo_id`,`estado_aseguramiento_id`) values 
(1,1,'000000000001','FE123','SIRAS-001234',1,NULL,'2023-08-15','14:30:00',1,'Av. Caracas con Cl 45','U',1,1);

/*Table structure for table `accidente_conductor` */

DROP TABLE IF EXISTS `accidente_conductor`;

CREATE TABLE `accidente_conductor` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK conductor vinculado',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `persona_id` bigint(20) unsigned NOT NULL COMMENT 'FK persona conductor',
  PRIMARY KEY (`id`),
  KEY `fk_accidente_conductor_acc` (`accidente_id`),
  KEY `fk_accidente_conductor_persona` (`persona_id`),
  CONSTRAINT `fk_accidente_conductor_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_conductor_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `accidente_conductor` */

insert  into `accidente_conductor`(`id`,`accidente_id`,`persona_id`) values 
(1,1,1);

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
  PRIMARY KEY (`id`),
  KEY `fk_accidente_detalle_acc` (`accidente_id`),
  KEY `fk_accidente_detalle_tipo` (`tipo_servicio_id`),
  KEY `fk_accidente_detalle_procedimiento` (`procedimiento_id`),
  CONSTRAINT `fk_accidente_detalle_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_detalle_procedimiento` FOREIGN KEY (`procedimiento_id`) REFERENCES `procedimiento` (`id`),
  CONSTRAINT `fk_accidente_detalle_tipo` FOREIGN KEY (`tipo_servicio_id`) REFERENCES `tipo_servicio` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `accidente_detalle` */

insert  into `accidente_detalle`(`id`,`accidente_id`,`tipo_servicio_id`,`procedimiento_id`,`codigo_servicio`,`descripcion`,`cantidad`,`valor_unitario`,`valor_facturado`,`valor_reclamado`) values 
(1,1,2,1,'15102','Desbridamiento por lesión',0,218000,218000,218000),
(2,1,2,1,'39003','15102-HONORARIOS CIRUJANO-GR-05',1,218000,218000,218000),
(3,1,2,1,'39103','15102-HONORARIOS ANESTESIA-GR-05',1,142500,142500,142500),
(4,1,2,1,'39207','15102-DERECHOS DE SALA -GR-05',1,388900,388900,388900),
(5,1,3,2,NULL,'Transporte primario ambulancia básica',1,120000,120000,120000);

/*Table structure for table `accidente_propietario` */

DROP TABLE IF EXISTS `accidente_propietario`;

CREATE TABLE `accidente_propietario` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK propietario vinculado',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `persona_id` bigint(20) unsigned NOT NULL COMMENT 'FK persona propietaria',
  PRIMARY KEY (`id`),
  KEY `fk_accidente_propietario_acc` (`accidente_id`),
  KEY `fk_accidente_propietario_persona` (`persona_id`),
  CONSTRAINT `fk_accidente_propietario_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_propietario_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `accidente_propietario` */

insert  into `accidente_propietario`(`id`,`accidente_id`,`persona_id`) values 
(1,1,1);

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_totales_accidente` (`accidente_id`),
  CONSTRAINT `fk_totales_accidente` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `accidente_totales` */

insert  into `accidente_totales`(`id`,`accidente_id`,`total_facturado_gmq`,`total_reclamado_gmq`,`total_facturado_transporte`,`total_reclamado_transporte`,`manifestacion_servicios`,`descripcion_evento`) values 
(1,1,908400,908400,120000,120000,1,'Accidente en Av. Caracas con Cl 45, víctima trasladada al primer centro de atención.');

/*Table structure for table `accidente_victima` */

DROP TABLE IF EXISTS `accidente_victima`;

CREATE TABLE `accidente_victima` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'PK víctima del accidente',
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente',
  `persona_id` bigint(20) unsigned NOT NULL COMMENT 'FK persona víctima',
  `condicion_codigo` char(1) DEFAULT NULL COMMENT '1 conductor, 2 peatón, 3 ocupante, 4 ciclista',
  `fecha_ingreso` datetime DEFAULT NULL COMMENT 'Fecha/hora de ingreso a IPS',
  `fecha_egreso` datetime DEFAULT NULL COMMENT 'Fecha/hora de egreso de IPS',
  `diagnostico_ingreso` char(4) DEFAULT NULL COMMENT 'CIE10 diagnóstico principal ingreso',
  `diagnostico_ingreso_sec1` char(4) DEFAULT NULL COMMENT 'CIE10 diagnóstico ingreso asociado 1',
  `diagnostico_ingreso_sec2` char(4) DEFAULT NULL COMMENT 'CIE10 diagnóstico ingreso asociado 2',
  `diagnostico_egreso` char(4) DEFAULT NULL COMMENT 'CIE10 diagnóstico principal egreso',
  `diagnostico_egreso_sec1` char(4) DEFAULT NULL COMMENT 'CIE10 diagnóstico egreso asociado 1',
  `diagnostico_egreso_sec2` char(4) DEFAULT NULL COMMENT 'CIE10 diagnóstico egreso asociado 2',
  `servicio_uci` tinyint(1) DEFAULT NULL COMMENT '0 no, 1 sí - uso de UCI',
  `dias_uci` smallint(5) unsigned DEFAULT NULL COMMENT 'Días en UCI',
  PRIMARY KEY (`id`),
  KEY `fk_accidente_victima_acc` (`accidente_id`),
  KEY `fk_accidente_victima_persona` (`persona_id`),
  CONSTRAINT `fk_accidente_victima_acc` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_accidente_victima_persona` FOREIGN KEY (`persona_id`) REFERENCES `persona` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `accidente_victima` */

insert  into `accidente_victima`(`id`,`accidente_id`,`persona_id`,`condicion_codigo`,`fecha_ingreso`,`fecha_egreso`,`diagnostico_ingreso`,`diagnostico_ingreso_sec1`,`diagnostico_ingreso_sec2`,`diagnostico_egreso`,`diagnostico_egreso_sec1`,`diagnostico_egreso_sec2`,`servicio_uci`,`dias_uci`) values 
(1,1,2,'3','2023-08-15 14:45:00','2023-08-17 10:00:00','S000',NULL,NULL,'S010',NULL,NULL,0,0);

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

/*Data for the table `departamento` */

insert  into `departamento`(`id`,`pais_id`,`codigo`,`nombre`,`estado`) values 
(1,1,'011','Bogotá D.C.',1),
(2,1,'076','Valle del Cauca',1);

/*Table structure for table `estado_aseguramiento` */

DROP TABLE IF EXISTS `estado_aseguramiento`;

CREATE TABLE `estado_aseguramiento` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK estado de aseguramiento',
  `codigo` char(1) NOT NULL COMMENT '1,2,3,4,6,7,8 según circular',
  `descripcion` varchar(60) NOT NULL COMMENT 'Descripción del estado de aseguramiento',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `estado_aseguramiento` */

insert  into `estado_aseguramiento`(`id`,`codigo`,`descripcion`) values 
(1,'1','Asegurado'),
(2,'2','No asegurado'),
(3,'3','Vehículo fantasma'),
(4,'4','Póliza falsa'),
(5,'6','Asegurado D.2497'),
(6,'7','No asegurado – propietario indeterminado'),
(7,'8','No asegurado – sin placa');

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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `municipio` */

insert  into `municipio`(`id`,`departamento_id`,`codigo_dane`,`codigo_postal`,`nombre`,`estado`) values 
(1,1,'11001','110111','Bogotá',1),
(2,2,'76001','760001','Cali',1);

/*Table structure for table `naturaleza_evento` */

DROP TABLE IF EXISTS `naturaleza_evento`;

CREATE TABLE `naturaleza_evento` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK naturaleza del evento',
  `codigo` char(2) NOT NULL COMMENT '01..27 según circular',
  `descripcion` varchar(60) NOT NULL COMMENT 'Descripción de la naturaleza',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `naturaleza_evento` */

insert  into `naturaleza_evento`(`id`,`codigo`,`descripcion`) values 
(1,'01','Accidente de tránsito'),
(2,'02','Sismo'),
(3,'03','Maremoto'),
(4,'04','Erupción volcánica'),
(5,'05','Deslizamiento de tierra'),
(6,'06','Inundación'),
(7,'07','Avalancha'),
(8,'08','Incendio natural'),
(9,'09','Explosión terrorista'),
(10,'10','Incendio terrorista'),
(11,'11','Combate'),
(12,'12','Ataques a Municipios'),
(13,'13','Masacre'),
(14,'14','Desplazados'),
(15,'15','Mina antipersonal'),
(16,'16','Huracán'),
(17,'17','Otro'),
(18,'25','Rayo'),
(19,'26','Vendaval'),
(20,'27','Tornado');

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

/*Data for the table `pais` */

insert  into `pais`(`id`,`codigo`,`nombre`,`estado`) values 
(1,'COL','Colombia',1),
(2,'VEN','Venezuela',1);

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_persona_doc` (`tipo_identificacion_id`,`numero_identificacion`),
  KEY `fk_persona_sexo` (`sexo_id`),
  KEY `fk_persona_municipio` (`municipio_residencia_id`),
  CONSTRAINT `fk_persona_municipio` FOREIGN KEY (`municipio_residencia_id`) REFERENCES `municipio` (`id`),
  CONSTRAINT `fk_persona_sexo` FOREIGN KEY (`sexo_id`) REFERENCES `sexo` (`id`),
  CONSTRAINT `fk_persona_tipo` FOREIGN KEY (`tipo_identificacion_id`) REFERENCES `tipo_identificacion` (`id`),
  CONSTRAINT `chk_persona_fallecimiento` CHECK (`fecha_fallecimiento` is null or `fecha_fallecimiento` >= `fecha_nacimiento`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `persona` */

insert  into `persona`(`id`,`tipo_identificacion_id`,`numero_identificacion`,`primer_nombre`,`segundo_nombre`,`primer_apellido`,`segundo_apellido`,`sexo_id`,`fecha_nacimiento`,`fecha_fallecimiento`,`direccion`,`telefono`,`municipio_residencia_id`,`fecha_registro`) values 
(1,1,'1012345678','Carlos','Andrés','Pérez','Gómez',2,'1990-05-12',NULL,'Cra 10 #20-30','3101234567',1,'2025-11-17 16:17:00'),
(2,6,'TI909090','María','Lucía','Rodríguez','López',1,'2007-08-03',NULL,'Cl 8 #12-45','3019876543',2,'2025-11-17 16:17:00'),
(3,1,'1122334455','Laura',NULL,'García','Martínez',1,'1985-02-18',NULL,'Av 68 #30-21','3001112233',1,'2025-11-17 16:17:00');

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_habilitacion` (`codigo_habilitacion`),
  KEY `fk_prestador_municipio` (`municipio_id`),
  CONSTRAINT `fk_prestador_municipio` FOREIGN KEY (`municipio_id`) REFERENCES `municipio` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `prestador_salud` */

insert  into `prestador_salud`(`id`,`codigo_habilitacion`,`razon_social`,`nit`,`telefono`,`municipio_id`,`direccion`) values 
(1,'123456789012','Clínica Central SAS','900123456','6015555555',1,'Cra 15 #100-20');

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

/*Data for the table `procedimiento` */

insert  into `procedimiento`(`id`,`codigo`,`descripcion`,`codigo_soat`,`valor`,`estado`,`es_traslado_primario`) values 
(1,'PR-39003','Honorarios cirujano grupo 5','39003',218000,'ACTIVO',0),
(2,'TP-0001','Transporte primario ambulancia básica',NULL,120000,'ACTIVO',1);

/*Table structure for table `sexo` */

DROP TABLE IF EXISTS `sexo`;

CREATE TABLE `sexo` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK sexo',
  `codigo` char(1) NOT NULL COMMENT 'F, M, O',
  `descripcion` varchar(15) NOT NULL COMMENT 'Descripción del sexo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `sexo` */

insert  into `sexo`(`id`,`codigo`,`descripcion`) values 
(1,'F','Femenino'),
(2,'M','Masculino'),
(3,'O','Otro');

/*Table structure for table `tipo_identificacion` */

DROP TABLE IF EXISTS `tipo_identificacion`;

CREATE TABLE `tipo_identificacion` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK tipo de identificación',
  `codigo` char(2) NOT NULL COMMENT 'Código (CC, CE, etc.)',
  `descripcion` varchar(50) NOT NULL COMMENT 'Descripción del tipo de documento',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `tipo_identificacion` */

insert  into `tipo_identificacion`(`id`,`codigo`,`descripcion`) values 
(1,'CC','Cédula de ciudadanía'),
(2,'CE','Cédula de extranjería'),
(3,'CN','Certificado de nacido vivo'),
(4,'PA','Pasaporte'),
(5,'RC','Registro civil'),
(6,'TI','Tarjeta de identidad'),
(7,'AS','Adulto sin identificación'),
(8,'MS','Menor sin identificación'),
(9,'PT','Permiso por protección temporal'),
(10,'PE','Permiso especial de permanencia'),
(11,'SC','Salvoconducto'),
(12,'CD','Carné diplomático'),
(13,'DE','Documento extranjero');

/*Table structure for table `tipo_servicio` */

DROP TABLE IF EXISTS `tipo_servicio`;

CREATE TABLE `tipo_servicio` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK tipo de servicio FURIPS2',
  `codigo` char(1) NOT NULL COMMENT '1..8 tipos de servicio',
  `descripcion` varchar(40) NOT NULL COMMENT 'Descripción del tipo de servicio',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `tipo_servicio` */

insert  into `tipo_servicio`(`id`,`codigo`,`descripcion`) values 
(1,'1','Medicamentos'),
(2,'2','Procedimientos'),
(3,'3','Transporte primario'),
(4,'4','Transporte secundario'),
(5,'5','Insumos'),
(6,'6','Dispositivos médicos'),
(7,'7','Material de osteosíntesis'),
(8,'8','Procedimiento no incluido en manual');

/*Table structure for table `tipo_vehiculo` */

DROP TABLE IF EXISTS `tipo_vehiculo`;

CREATE TABLE `tipo_vehiculo` (
  `id` tinyint(3) unsigned NOT NULL COMMENT 'PK tipo de vehículo',
  `codigo` char(2) NOT NULL COMMENT 'Código de tipo de vehículo',
  `descripcion` varchar(40) NOT NULL COMMENT 'Descripción del tipo de vehículo',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `tipo_vehiculo` */

insert  into `tipo_vehiculo`(`id`,`codigo`,`descripcion`) values 
(1,'01','Automóvil'),
(2,'02','Bus'),
(3,'03','Buseta'),
(4,'04','Camión'),
(5,'05','Camioneta'),
(6,'06','Campero'),
(7,'07','Microbús'),
(8,'08','Tractocamión'),
(9,'10','Motocicleta'),
(10,'14','Motocarro'),
(11,'17','Mototriciclo'),
(12,'19','Cuatrimoto'),
(13,'20','Moto extranjera'),
(14,'21','Vehículo extranjero'),
(15,'22','Volqueta');

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `placa` (`placa`),
  KEY `fk_vehiculo_tipo` (`tipo_vehiculo_id`),
  KEY `fk_vehiculo_estado` (`estado_aseguramiento_id`),
  KEY `fk_vehiculo_propietario` (`propietario_id`),
  CONSTRAINT `fk_vehiculo_estado` FOREIGN KEY (`estado_aseguramiento_id`) REFERENCES `estado_aseguramiento` (`id`),
  CONSTRAINT `fk_vehiculo_propietario` FOREIGN KEY (`propietario_id`) REFERENCES `persona` (`id`),
  CONSTRAINT `fk_vehiculo_tipo` FOREIGN KEY (`tipo_vehiculo_id`) REFERENCES `tipo_vehiculo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

/*Data for the table `vehiculo` */

insert  into `vehiculo`(`id`,`placa`,`marca`,`tipo_vehiculo_id`,`aseguradora_codigo`,`numero_poliza`,`vigencia_inicio`,`vigencia_fin`,`estado_aseguramiento_id`,`propietario_id`) values 
(1,'ABC123','Chevrolet',1,'AT0012','SOAT-456789','2023-01-01','2023-12-31',1,1);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
