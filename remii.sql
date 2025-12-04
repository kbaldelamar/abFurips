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

/*Table structure for table `accidente_remision` */

DROP TABLE IF EXISTS `accidente_remision`;

CREATE TABLE `accidente_remision` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `accidente_id` bigint(20) unsigned NOT NULL COMMENT 'FK accidente (padre)',
  `tipo_referencia` tinyint(4) NOT NULL COMMENT '1 = Remite paciente, 2 = Orden de servicio, 3 = Recibe paciente',
  `fecha_remision` date DEFAULT NULL,
  `hora_salida` time DEFAULT NULL,
  `fecha_aceptacion` date DEFAULT NULL,
  `hora_aceptacion` time DEFAULT NULL,
  `ipsRecibe` varchar(100) NOT NULL,
  `codigo_hab_recibe` varchar(12) DEFAULT NULL,
  `profesional_recibe` varchar(60) DEFAULT NULL,
  `cargo_Recibe` varchar(100) DEFAULT NULL,
  `placa_ambulancia` varchar(12) DEFAULT NULL,
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo',
  `persona_remite_id` bigint(20) unsigned DEFAULT NULL,
  `creado_en` timestamp NULL DEFAULT current_timestamp(),
  `actualizado_en` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `prestadorId` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`,`prestadorId`),
  KEY `fk_acc_rem_accidente` (`accidente_id`),
  KEY `fk_acc_rem_persona_remite` (`persona_remite_id`),
  CONSTRAINT `fk_acc_rem_accidente` FOREIGN KEY (`accidente_id`) REFERENCES `accidente` (`id`),
  CONSTRAINT `fk_acc_rem_persona_remite` FOREIGN KEY (`persona_remite_id`) REFERENCES `persona` (`id`),
  CONSTRAINT `chk_acc_rem_tipo` CHECK (`tipo_referencia` in (1,2,3))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

/*Data for the table `accidente_remision` */

insert  into `accidente_remision`(`id`,`accidente_id`,`tipo_referencia`,`fecha_remision`,`hora_salida`,`fecha_aceptacion`,`hora_aceptacion`,`ipsRecibe`,`codigo_hab_recibe`,`profesional_recibe`,`cargo_Recibe`,`placa_ambulancia`,`estado`,`persona_remite_id`,`creado_en`,`actualizado_en`,`prestadorId`) values 
(1,11,1,'2025-11-30','14:58:19','2025-11-30','14:58:19','','123123','willian',NULL,'1231231','activo',7,'2025-11-30 20:36:12','2025-11-30 20:47:30',1);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
