-- MySQL dump 10.13  Distrib 5.5.43, for debian-linux-gnu (armv7l)
--
-- Host: localhost    Database: medbox
-- ------------------------------------------------------
-- Server version	5.5.43-0+deb7u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `medbox`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `medbox` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `medbox`;

--
-- Table structure for table `bin`
--

DROP TABLE IF EXISTS `bin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bin` (
  `count` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `angle` float(6,3) unsigned NOT NULL DEFAULT '0.000',
  `drug_ndc` bigint(10) unsigned DEFAULT NULL,
  `equipt_upn` varchar(20) DEFAULT NULL,
  `box_id` bigint(20) unsigned NOT NULL,
  `pos` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `fk_drug_ndc` (`drug_ndc`),
  KEY `fk_equipt_upn` (`equipt_upn`),
  KEY `fk_box_id` (`box_id`),
  CONSTRAINT `fk_box_id` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`),
  CONSTRAINT `fk_drug_ndc` FOREIGN KEY (`drug_ndc`) REFERENCES `drug` (`ndc`),
  CONSTRAINT `fk_equipt_upn` FOREIGN KEY (`equipt_upn`) REFERENCES `equipt` (`upn`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bin`
--

LOCK TABLES `bin` WRITE;
/*!40000 ALTER TABLE `bin` DISABLE KEYS */;
INSERT INTO `bin` VALUES (3,0.000,364904802,NULL,1,0,1),(0,0.000,NULL,'testupn',1,1,2);
/*!40000 ALTER TABLE `bin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `box`
--

DROP TABLE IF EXISTS `box`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `box` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `mode` tinyint(1) DEFAULT '0',
  `open` tinyint(1) DEFAULT '0',
  `latitude` double(10,8) DEFAULT NULL,
  `longitude` double(11,8) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `box`
--

LOCK TABLES `box` WRITE;
/*!40000 ALTER TABLE `box` DISABLE KEYS */;
INSERT INTO `box` VALUES (1,0,0,NULL,NULL);
/*!40000 ALTER TABLE `box` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drug`
--

DROP TABLE IF EXISTS `drug`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `drug` (
  `brand_name` varchar(80) NOT NULL,
  `gen_name` varchar(100) NOT NULL,
  `schedule` tinyint(1) DEFAULT NULL,
  `route` varchar(50) NOT NULL,
  `dosage` varchar(24) NOT NULL,
  `ndc` bigint(10) unsigned NOT NULL,
  `max_count` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `weight` float(8,5) unsigned NOT NULL DEFAULT '0.50000',
  PRIMARY KEY (`ndc`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drug`
--

LOCK TABLES `drug` WRITE;
/*!40000 ALTER TABLE `drug` DISABLE KEYS */;
INSERT INTO `drug` VALUES ('Septocaine and Epinephrine','Aticane Hydrochloride and Epinepherine Bitartrate',NULL,'SUBCUTANEOUS','40 mg/ml, .005 mg/ml',364904802,0,0.50000);
/*!40000 ALTER TABLE `drug` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipt`
--

DROP TABLE IF EXISTS `equipt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `equipt` (
  `upn` varchar(20) NOT NULL,
  `name` varchar(80) NOT NULL,
  `max_count` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `weight` float(8,5) unsigned NOT NULL DEFAULT '0.50000',
  PRIMARY KEY (`upn`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipt`
--

LOCK TABLES `equipt` WRITE;
/*!40000 ALTER TABLE `equipt` DISABLE KEYS */;
INSERT INTO `equipt` VALUES ('testupn','syringe',1,0.50000);
/*!40000 ALTER TABLE `equipt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kit`
--

DROP TABLE IF EXISTS `kit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kit` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `drug_ndc` bigint(10) unsigned DEFAULT NULL,
  `equipt_upn` varchar(20) DEFAULT NULL,
  `score` float(5,2) NOT NULL DEFAULT '50.00',
  PRIMARY KEY (`id`),
  KEY `drug_ndc` (`drug_ndc`),
  KEY `equipt_upn` (`equipt_upn`),
  CONSTRAINT `kit_ibfk_1` FOREIGN KEY (`drug_ndc`) REFERENCES `drug` (`ndc`),
  CONSTRAINT `kit_ibfk_2` FOREIGN KEY (`equipt_upn`) REFERENCES `equipt` (`upn`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kit`
--

LOCK TABLES `kit` WRITE;
/*!40000 ALTER TABLE `kit` DISABLE KEYS */;
INSERT INTO `kit` VALUES (1,'ANAPHYLAXIS',364904802,NULL,50.00),(3,'ANAPHYLAXIS',NULL,'testupn',50.00);
/*!40000 ALTER TABLE `kit` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 trigger InsertKitDrugEquiptNotNull BEFORE INSERT ON kit FOR EACH ROW BEGIN IF (NEW.drug_ndc IS NULL AND NEW.equipt_upn IS NULL) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'INSERT IN KIT REQUIRES EITHER A drug_ndc OR A equipt_upn TO BE ENTERED'; END IF; END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 trigger UpdateKitDrugEquiptNotNull BEFORE UPDATE ON kit FOR EACH ROW BEGIN IF (NEW.drug_ndc IS NULL AND NEW.equipt_upn IS NULL) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'INSERT IN KIT REQUIRES EITHER A drug_ndc OR A equipt_upn TO BE ENTERED'; END IF; END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `logbox`
--

DROP TABLE IF EXISTS `logbox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logbox` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `tm` datetime NOT NULL,
  `latitude` double(10,8) NOT NULL,
  `longitude` double(11,8) NOT NULL,
  `drug_ndc` bigint(10) unsigned DEFAULT NULL,
  `box_id` bigint(20) unsigned NOT NULL,
  `event` varchar(50) NOT NULL,
  `rfid_id` int(10) unsigned DEFAULT NULL,
  `mode` tinyint(1) DEFAULT '1',
  `equipt_upn` varchar(20) DEFAULT NULL,
  `code` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_log_drug_ndc` (`drug_ndc`),
  KEY `fk_log_box_id` (`box_id`),
  KEY `fk_log_rfid_id` (`rfid_id`),
  KEY `fk_logbox_equipt_upn` (`equipt_upn`),
  CONSTRAINT `fk_logbox_equipt_upn` FOREIGN KEY (`equipt_upn`) REFERENCES `equipt` (`upn`),
  CONSTRAINT `fk_log_box_id` FOREIGN KEY (`box_id`) REFERENCES `box` (`id`),
  CONSTRAINT `fk_log_drug_ndc` FOREIGN KEY (`drug_ndc`) REFERENCES `drug` (`ndc`),
  CONSTRAINT `fk_log_rfid_id` FOREIGN KEY (`rfid_id`) REFERENCES `rfid` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logbox`
--

LOCK TABLES `logbox` WRITE;
/*!40000 ALTER TABLE `logbox` DISABLE KEYS */;
INSERT INTO `logbox` VALUES (76,'2015-05-18 15:31:19',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH 1',NULL,1,NULL,-1),(77,'2015-05-18 15:31:23',0.00000000,0.00000000,NULL,1,'ALERT: BIN OPENED WHILE BOX NOT AUTHORIZED TO OPEN',NULL,1,NULL,0),(78,'2015-05-18 15:31:24',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',NULL,-1,'testupn',1),(79,'2015-05-18 15:31:31',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH ',NULL,1,NULL,-1),(80,'2015-05-18 15:33:04',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH 5',NULL,1,NULL,-1),(81,'2015-05-18 15:33:29',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH dir()',NULL,1,NULL,-1),(82,'2015-05-18 15:34:45',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH 5',NULL,1,NULL,-1),(83,'2015-05-18 15:34:47',0.00000000,0.00000000,NULL,1,'ALERT: BIN OPENED WHILE BOX NOT AUTHORIZED TO OPEN',NULL,1,NULL,0),(84,'2015-05-18 15:34:47',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',NULL,-1,'testupn',1),(85,'2015-05-18 20:08:16',0.00000000,0.00000000,NULL,1,'BOX: SUCESS OPEN',1,1,NULL,0),(86,'2015-05-18 20:08:30',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(87,'2015-05-18 20:08:39',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',1,1,'testupn',1),(88,'2015-05-18 20:09:28',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH ',NULL,1,NULL,-1),(89,'2015-05-18 20:09:37',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(90,'2015-05-18 20:09:40',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(91,'2015-05-18 20:09:42',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',1,1,'testupn',1),(92,'2015-05-18 20:11:03',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH 5',NULL,1,NULL,-1),(93,'2015-05-18 20:11:05',0.00000000,0.00000000,NULL,1,'BOX: OPENED',NULL,1,NULL,0),(94,'2015-05-18 20:11:05',0.00000000,0.00000000,NULL,1,'ALERT: BOX OPEN WHILE NOT AUTHORIZED',NULL,1,NULL,0),(95,'2015-05-18 20:11:15',0.00000000,0.00000000,NULL,1,'ALERT: BOX OPEN WHILE NOT IN ACTIVE MODE',NULL,1,NULL,0),(96,'2015-05-18 20:11:15',0.00000000,0.00000000,NULL,1,'ALERT: BOX OPEN WHILE NOT AUTHORIZED',NULL,1,NULL,0),(97,'2015-05-18 20:11:15',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',NULL,-1,'testupn',1),(98,'2015-05-18 20:13:04',0.00000000,0.00000000,NULL,1,'BOX: SUCESS OPEN',1,1,NULL,0),(99,'2015-05-18 20:13:10',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(100,'2015-05-18 20:13:21',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH 555',NULL,1,NULL,-1),(101,'2015-05-18 20:13:25',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(102,'2015-05-18 20:16:49',0.00000000,0.00000000,NULL,1,'BOX: SUCESS OPEN',1,1,NULL,0),(103,'2015-05-18 20:16:52',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(104,'2015-05-18 20:16:56',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',1,1,'testupn',1),(105,'2015-05-18 20:17:01',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(106,'2015-05-18 20:17:07',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',1,1,'testupn',1),(107,'2015-05-18 20:17:16',0.00000000,0.00000000,NULL,1,'DEC ERROR: OUT OF ITEM',1,1,'testupn',1),(108,'2015-05-18 20:17:26',0.00000000,0.00000000,NULL,1,'BOX: CLOSED',1,1,NULL,0),(109,'2015-05-18 20:17:29',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH 4',NULL,1,NULL,-1),(110,'2015-05-18 20:17:32',0.00000000,0.00000000,NULL,1,'BOX: OPENED',1,1,NULL,0),(111,'2015-05-18 20:17:32',0.00000000,0.00000000,NULL,1,'ALERT: BOX OPEN WHILE NOT AUTHORIZED',1,1,NULL,0),(112,'2015-05-18 20:18:11',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN UNKNOWN AUTH 5',NULL,1,NULL,-1),(113,'2015-05-18 20:18:13',0.00000000,0.00000000,NULL,1,'BOX: OPENED',NULL,1,NULL,0),(114,'2015-05-18 20:18:13',0.00000000,0.00000000,NULL,1,'ALERT: BOX OPEN WHILE NOT AUTHORIZED',NULL,1,NULL,0),(115,'2015-05-19 17:35:21',0.00000000,0.00000000,NULL,1,'BOX: SUCESS OPEN',1,1,NULL,0),(116,'2015-05-19 18:08:04',0.00000000,0.00000000,NULL,1,'BOX: SUCESS OPEN',3,1,NULL,0),(117,'2015-05-19 18:11:15',0.00000000,0.00000000,NULL,1,'BOX: SUCESS OPEN',3,1,NULL,0),(118,'2015-05-19 18:13:42',0.00000000,0.00000000,NULL,1,'BOX: SUCESS OPEN',3,1,NULL,0),(119,'2015-05-19 18:13:58',0.00000000,0.00000000,NULL,1,'BOX: FAIL OPEN BAD AUTH',5,1,NULL,-1);
/*!40000 ALTER TABLE `logbox` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `other`
--

DROP TABLE IF EXISTS `other`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `other` (
  `rfid_id` int(10) unsigned NOT NULL,
  `data` varchar(290) NOT NULL,
  UNIQUE KEY `data` (`data`),
  UNIQUE KEY `data_2` (`data`),
  KEY `rfid_id` (`rfid_id`),
  CONSTRAINT `other_ibfk_1` FOREIGN KEY (`rfid_id`) REFERENCES `rfid` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `other`
--

LOCK TABLES `other` WRITE;
/*!40000 ALTER TABLE `other` DISABLE KEYS */;
INSERT INTO `other` VALUES (3,'04a8008885fd954676422806f5efcc4f881e026c46058b5e7815c475f7dc2611a1ac32d1b9c84d4cfb6cbb4ec271376585791eba885c62b1020239da0667c14e:db61b6f16cbd4d4bb6d6633b121bf7d9:b93c3450215912c928a4209f73151bd798f3f648dfe145eb94bc8e1bc8b9a789d461d03ed9737000074bb590a8af196e8d65aa4ce952ec884bb7e9181b6469eb');
/*!40000 ALTER TABLE `other` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rfid`
--

DROP TABLE IF EXISTS `rfid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rfid` (
  `data` varchar(161) NOT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `worker_id` bigint(20) unsigned DEFAULT NULL,
  `auth` tinyint(1) NOT NULL DEFAULT '-1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `data` (`data`),
  KEY `fk_rfid_worker_id` (`worker_id`),
  CONSTRAINT `fk_rfid_worker_id` FOREIGN KEY (`worker_id`) REFERENCES `worker` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rfid`
--

LOCK TABLES `rfid` WRITE;
/*!40000 ALTER TABLE `rfid` DISABLE KEYS */;
INSERT INTO `rfid` VALUES ('736047c478a399f3c033c20a8ef285214e86a8b7d05f823076c8f0e15adad32e9704f8c79ea3f9ca9411ff372b9bcb1bd0d0b0ff42c0e13dd00a557158e4124a:327b71d1b8424f158559c5ec2fece5da',1,1,1),('c9031f2675a5031ee6f4e1cdd8172d096da1d8c4370e8632e25d1ff6da3194909c9a5a8d9fdc20d8ccfcc0fd31622d0de1caacce86879a688830acc48460e3f7:352974e6a42e4613a73c4d969e59fcaf',3,2,2),('adba8969e491492ff54e07fb6ce1805e7de98e03f4ad8a21887ae6a3aa7060651d2271f90f1d8aee282b0679f9fa7dd724dc842df37fe8137020966d4918bb01:c76f8fa4202a440eb1ff3a8fe9b78389',4,3,0),('b02a4bc84878f7ac81ee256c5d72ae5851a3ce2e36e9f6f3fc280e6384fcaeeaf1eb0540fe70869e2edb1bc09074950fee0fc7732e8ae99d3f66af5bd6d994b5:3ab7ad7bac034523baee3ed09b6d8c8d',5,4,-1);
/*!40000 ALTER TABLE `rfid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `worker`
--

DROP TABLE IF EXISTS `worker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `worker` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `employer_id` bigint(20) unsigned NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `worker`
--

LOCK TABLES `worker` WRITE;
/*!40000 ALTER TABLE `worker` DISABLE KEYS */;
INSERT INTO `worker` VALUES (1,'Joe Test',1,'7678689-45'),(2,'SUPERVISOR TEST',2,'igyg-5656'),(3,'STOCKER TEST',1,'78565-886-5656'),(4,'INACTIVE TEST',4,'8b689-5656');
/*!40000 ALTER TABLE `worker` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-05-19 20:32:50
