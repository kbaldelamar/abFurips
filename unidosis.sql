/*
SQLyog Ultimate v12.4.3 (64 bit)
MySQL - 11.4.2-MariaDB-log : Database - baseserver
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`baseserver` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

/*Table structure for table `h_ordenes_unidosis_detalle_aplicacion` */

DROP TABLE IF EXISTS `h_ordenes_unidosis_detalle_aplicacion`;

CREATE TABLE `h_ordenes_unidosis_detalle_aplicacion` (
  `Id_Ordenes_UDetalle` bigint(20) unsigned NOT NULL,
  `Fecha_A` date DEFAULT NULL,
  `Hora` time DEFAULT NULL,
  `Id_Profesional` mediumint(9) unsigned NOT NULL,
  `Id_Especialidad` mediumint(9) unsigned NOT NULL,
  `Observacion` mediumtext DEFAULT NULL,
  `Estado` tinyint(1) DEFAULT 1,
  `Fecha` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `UsuarioS` varchar(50) DEFAULT '',
  `Id_Remoto` bigint(19) DEFAULT 0 COMMENT 'Id en la bd del servidor',
  PRIMARY KEY (`Id_Ordenes_UDetalle`),
  CONSTRAINT `FK_h_ordenes_unidosis_detalle_aplicacion_ap` FOREIGN KEY (`Id_Ordenes_UDetalle`) REFERENCES `h_ordenes_unidosis_detalle` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*Data for the table `h_ordenes_unidosis_detalle_aplicacion` */

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
