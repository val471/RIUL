-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: riul
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrador`
--

DROP TABLE IF EXISTS `administrador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrador` (
  `id_usuario` int NOT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrador`
--

LOCK TABLES `administrador` WRITE;
/*!40000 ALTER TABLE `administrador` DISABLE KEYS */;
/*!40000 ALTER TABLE `administrador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `archivo`
--

DROP TABLE IF EXISTS `archivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `archivo` (
  `id_archivo` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `id_publicacion` int DEFAULT NULL,
  `id_evidencia` int DEFAULT NULL,
  `id_avance` int DEFAULT NULL,
  `id_comentario` int DEFAULT NULL,
  `nombre_original` varchar(150) NOT NULL,
  `ruta` varchar(255) NOT NULL,
  `tipo_archivo` varchar(20) NOT NULL,
  `peso_archivo` int NOT NULL,
  `fecha_carga` datetime NOT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_archivo`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_publicacion` (`id_publicacion`),
  KEY `id_evidencia` (`id_evidencia`),
  KEY `id_avance` (`id_avance`),
  KEY `id_comentario` (`id_comentario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archivo`
--

LOCK TABLES `archivo` WRITE;
/*!40000 ALTER TABLE `archivo` DISABLE KEYS */;
/*!40000 ALTER TABLE `archivo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `avanceproyecto`
--

DROP TABLE IF EXISTS `avanceproyecto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `avanceproyecto` (
  `id_avance` int NOT NULL AUTO_INCREMENT,
  `id_proyecto` int NOT NULL,
  `descripcion` text,
  `fecha` datetime NOT NULL,
  PRIMARY KEY (`id_avance`),
  KEY `id_proyecto` (`id_proyecto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `avanceproyecto`
--

LOCK TABLES `avanceproyecto` WRITE;
/*!40000 ALTER TABLE `avanceproyecto` DISABLE KEYS */;
/*!40000 ALTER TABLE `avanceproyecto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comentario`
--

DROP TABLE IF EXISTS `comentario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comentario` (
  `id_comentario` int NOT NULL AUTO_INCREMENT,
  `id_publicacion` int NOT NULL,
  `id_usuario` int NOT NULL,
  `contenido` text NOT NULL,
  `fecha` datetime NOT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_comentario`),
  KEY `id_publicacion` (`id_publicacion`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comentario`
--

LOCK TABLES `comentario` WRITE;
/*!40000 ALTER TABLE `comentario` DISABLE KEYS */;
/*!40000 ALTER TABLE `comentario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compartido`
--

DROP TABLE IF EXISTS `compartido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compartido` (
  `id_compartido` int NOT NULL AUTO_INCREMENT,
  `id_publicacion` int NOT NULL,
  `id_usuario` int NOT NULL,
  `fecha` datetime NOT NULL,
  PRIMARY KEY (`id_compartido`),
  KEY `id_publicacion` (`id_publicacion`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compartido`
--

LOCK TABLES `compartido` WRITE;
/*!40000 ALTER TABLE `compartido` DISABLE KEYS */;
/*!40000 ALTER TABLE `compartido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `convocatoria`
--

DROP TABLE IF EXISTS `convocatoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `convocatoria` (
  `id_convocatoria` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(150) NOT NULL,
  `descripcion` text,
  `fecha_inicio` date NOT NULL,
  `fecha_cierre` date NOT NULL,
  `modalidad` enum('semillero','individual','ambas') NOT NULL,
  `estado` varchar(20) NOT NULL,
  `id_admin_creador` int NOT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_convocatoria`),
  KEY `id_admin_creador` (`id_admin_creador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `convocatoria`
--

LOCK TABLES `convocatoria` WRITE;
/*!40000 ALTER TABLE `convocatoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `convocatoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `docentelider`
--

DROP TABLE IF EXISTS `docentelider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `docentelider` (
  `id_usuario` int NOT NULL,
  `id_semillero_liderado` int DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `id_semillero_liderado` (`id_semillero_liderado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `docentelider`
--

LOCK TABLES `docentelider` WRITE;
/*!40000 ALTER TABLE `docentelider` DISABLE KEYS */;
/*!40000 ALTER TABLE `docentelider` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estudianteinvestigador`
--

DROP TABLE IF EXISTS `estudianteinvestigador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estudianteinvestigador` (
  `id_usuario` int NOT NULL,
  `codigo_estudiantil` varchar(30) NOT NULL,
  `id_programa` int NOT NULL,
  `semestre` int NOT NULL,
  `id_semillero` int DEFAULT NULL,
  `xp_total` int NOT NULL,
  `id_nivel_actual` int DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `codigo_estudiantil` (`codigo_estudiantil`),
  KEY `id_programa` (`id_programa`),
  KEY `id_semillero` (`id_semillero`),
  KEY `id_nivel_actual` (`id_nivel_actual`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estudianteinvestigador`
--

LOCK TABLES `estudianteinvestigador` WRITE;
/*!40000 ALTER TABLE `estudianteinvestigador` DISABLE KEYS */;
/*!40000 ALTER TABLE `estudianteinvestigador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evento`
--

DROP TABLE IF EXISTS `evento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evento` (
  `id_evento` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `fecha` datetime NOT NULL,
  `lugar` varchar(150) DEFAULT NULL,
  `modalidad` enum('semillero','individual','ambas') NOT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_evento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evento`
--

LOCK TABLES `evento` WRITE;
/*!40000 ALTER TABLE `evento` DISABLE KEYS */;
/*!40000 ALTER TABLE `evento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencia`
--

DROP TABLE IF EXISTS `evidencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencia` (
  `id_evidencia` int NOT NULL AUTO_INCREMENT,
  `id_logro` int NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL,
  PRIMARY KEY (`id_evidencia`),
  KEY `id_logro` (`id_logro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia`
--

LOCK TABLES `evidencia` WRITE;
/*!40000 ALTER TABLE `evidencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `evidencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facultad`
--

DROP TABLE IF EXISTS `facultad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facultad` (
  `id_facultad` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `id_admin_gestor` int DEFAULT NULL,
  PRIMARY KEY (`id_facultad`),
  KEY `id_admin_gestor` (`id_admin_gestor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facultad`
--

LOCK TABLES `facultad` WRITE;
/*!40000 ALTER TABLE `facultad` DISABLE KEYS */;
/*!40000 ALTER TABLE `facultad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial`
--

DROP TABLE IF EXISTS `historial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial` (
  `id_historial` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `accion` varchar(50) NOT NULL,
  `tabla_afectada` varchar(50) NOT NULL,
  `id_registro` int NOT NULL,
  `valor_anterior` text,
  `valor_nuevo` text,
  `fecha` datetime NOT NULL,
  PRIMARY KEY (`id_historial`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial`
--

LOCK TABLES `historial` WRITE;
/*!40000 ALTER TABLE `historial` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historialxp`
--

DROP TABLE IF EXISTS `historialxp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historialxp` (
  `id_historial_xp` int NOT NULL AUTO_INCREMENT,
  `id_estudiante` int DEFAULT NULL,
  `id_semillero` int DEFAULT NULL,
  `id_logro` int NOT NULL,
  `cantidad_xp` int NOT NULL,
  `fecha` datetime NOT NULL,
  PRIMARY KEY (`id_historial_xp`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_semillero` (`id_semillero`),
  KEY `id_logro` (`id_logro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historialxp`
--

LOCK TABLES `historialxp` WRITE;
/*!40000 ALTER TABLE `historialxp` DISABLE KEYS */;
/*!40000 ALTER TABLE `historialxp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inscripcionconvocatoria`
--

DROP TABLE IF EXISTS `inscripcionconvocatoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inscripcionconvocatoria` (
  `id_inscripcion` int NOT NULL AUTO_INCREMENT,
  `id_convocatoria` int NOT NULL,
  `id_estudiante` int DEFAULT NULL,
  `id_semillero` int DEFAULT NULL,
  `fecha_inscripcion` datetime NOT NULL,
  PRIMARY KEY (`id_inscripcion`),
  KEY `id_convocatoria` (`id_convocatoria`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_semillero` (`id_semillero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inscripcionconvocatoria`
--

LOCK TABLES `inscripcionconvocatoria` WRITE;
/*!40000 ALTER TABLE `inscripcionconvocatoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `inscripcionconvocatoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insignia`
--

DROP TABLE IF EXISTS `insignia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insignia` (
  `id_insignia` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `tipo` varchar(20) NOT NULL,
  `grado` varchar(10) NOT NULL,
  `xp_requerido` int NOT NULL,
  PRIMARY KEY (`id_insignia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insignia`
--

LOCK TABLES `insignia` WRITE;
/*!40000 ALTER TABLE `insignia` DISABLE KEYS */;
/*!40000 ALTER TABLE `insignia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insigniaotorgada`
--

DROP TABLE IF EXISTS `insigniaotorgada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insigniaotorgada` (
  `id_usuario_insignia` int NOT NULL AUTO_INCREMENT,
  `id_insignia` int NOT NULL,
  `id_usuario` int DEFAULT NULL,
  `id_semillero` int DEFAULT NULL,
  `fecha_obtencion` datetime NOT NULL,
  PRIMARY KEY (`id_usuario_insignia`),
  KEY `id_insignia` (`id_insignia`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_semillero` (`id_semillero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insigniaotorgada`
--

LOCK TABLES `insigniaotorgada` WRITE;
/*!40000 ALTER TABLE `insigniaotorgada` DISABLE KEYS */;
/*!40000 ALTER TABLE `insigniaotorgada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logro`
--

DROP TABLE IF EXISTS `logro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logro` (
  `id_logro` int NOT NULL AUTO_INCREMENT,
  `id_tipo_logro` int NOT NULL,
  `descripcion` text,
  `id_estudiante` int DEFAULT NULL,
  `id_semillero` int DEFAULT NULL,
  `id_docente_registrador` int DEFAULT NULL,
  `estado` varchar(20) NOT NULL,
  `id_admin_validador` int DEFAULT NULL,
  `fecha_registro` datetime NOT NULL,
  `fecha_validacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_logro`),
  KEY `id_tipo_logro` (`id_tipo_logro`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_semillero` (`id_semillero`),
  KEY `id_docente_registrador` (`id_docente_registrador`),
  KEY `id_admin_validador` (`id_admin_validador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logro`
--

LOCK TABLES `logro` WRITE;
/*!40000 ALTER TABLE `logro` DISABLE KEYS */;
/*!40000 ALTER TABLE `logro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `membresiasemillero`
--

DROP TABLE IF EXISTS `membresiasemillero`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membresiasemillero` (
  `id_membresia` int NOT NULL AUTO_INCREMENT,
  `id_estudiante` int NOT NULL,
  `id_semillero` int NOT NULL,
  `fecha_ingreso` datetime NOT NULL,
  `fecha_salida` datetime DEFAULT NULL,
  PRIMARY KEY (`id_membresia`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_semillero` (`id_semillero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membresiasemillero`
--

LOCK TABLES `membresiasemillero` WRITE;
/*!40000 ALTER TABLE `membresiasemillero` DISABLE KEYS */;
/*!40000 ALTER TABLE `membresiasemillero` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nivel`
--

DROP TABLE IF EXISTS `nivel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nivel` (
  `id_nivel` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `estrellas` int NOT NULL,
  `insignias_minimas` int NOT NULL,
  `tipo` varchar(20) NOT NULL,
  PRIMARY KEY (`id_nivel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nivel`
--

LOCK TABLES `nivel` WRITE;
/*!40000 ALTER TABLE `nivel` DISABLE KEYS */;
/*!40000 ALTER TABLE `nivel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificacion`
--

DROP TABLE IF EXISTS `notificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificacion` (
  `id_notificacion` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `mensaje` text NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `fecha` datetime NOT NULL,
  PRIMARY KEY (`id_notificacion`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificacion`
--

LOCK TABLES `notificacion` WRITE;
/*!40000 ALTER TABLE `notificacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `notificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `participacionevento`
--

DROP TABLE IF EXISTS `participacionevento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `participacionevento` (
  `id_participacion` int NOT NULL AUTO_INCREMENT,
  `id_evento` int NOT NULL,
  `id_usuario` int NOT NULL,
  `id_semillero` int DEFAULT NULL,
  `tipo_participacion` varchar(30) NOT NULL,
  `fecha_registro` datetime NOT NULL,
  PRIMARY KEY (`id_participacion`),
  KEY `id_evento` (`id_evento`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_semillero` (`id_semillero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `participacionevento`
--

LOCK TABLES `participacionevento` WRITE;
/*!40000 ALTER TABLE `participacionevento` DISABLE KEYS */;
/*!40000 ALTER TABLE `participacionevento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `programa`
--

DROP TABLE IF EXISTS `programa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `programa` (
  `id_programa` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `id_facultad` int NOT NULL,
  `id_admin_gestor` int DEFAULT NULL,
  PRIMARY KEY (`id_programa`),
  KEY `id_facultad` (`id_facultad`),
  KEY `id_admin_gestor` (`id_admin_gestor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `programa`
--

LOCK TABLES `programa` WRITE;
/*!40000 ALTER TABLE `programa` DISABLE KEYS */;
/*!40000 ALTER TABLE `programa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto`
--

DROP TABLE IF EXISTS `proyecto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto` (
  `id_proyecto` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(150) NOT NULL,
  `descripcion` text,
  `id_semillero` int NOT NULL,
  `fecha_inicio` date NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_proyecto`),
  KEY `id_semillero` (`id_semillero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto`
--

LOCK TABLES `proyecto` WRITE;
/*!40000 ALTER TABLE `proyecto` DISABLE KEYS */;
/*!40000 ALTER TABLE `proyecto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `publicacion`
--

DROP TABLE IF EXISTS `publicacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `publicacion` (
  `id_publicacion` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `id_semillero` int DEFAULT NULL,
  `contenido` text NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `tipo_publicacion` varchar(10) NOT NULL,
  `vistas` int NOT NULL,
  `fecha_publicacion` datetime NOT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_publicacion`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_semillero` (`id_semillero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `publicacion`
--

LOCK TABLES `publicacion` WRITE;
/*!40000 ALTER TABLE `publicacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `publicacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ranking`
--

DROP TABLE IF EXISTS `ranking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ranking` (
  `id_ranking` int NOT NULL AUTO_INCREMENT,
  `id_estudiante` int DEFAULT NULL,
  `id_semillero` int DEFAULT NULL,
  `id_nivel` int NOT NULL,
  `posicion` int NOT NULL,
  `fecha_actualizacion` datetime NOT NULL,
  PRIMARY KEY (`id_ranking`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_semillero` (`id_semillero`),
  KEY `id_nivel` (`id_nivel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ranking`
--

LOCK TABLES `ranking` WRITE;
/*!40000 ALTER TABLE `ranking` DISABLE KEYS */;
/*!40000 ALTER TABLE `ranking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reaccion`
--

DROP TABLE IF EXISTS `reaccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reaccion` (
  `id_reaccion` int NOT NULL AUTO_INCREMENT,
  `id_publicacion` int NOT NULL,
  `id_usuario` int NOT NULL,
  `fecha` datetime NOT NULL,
  PRIMARY KEY (`id_reaccion`),
  KEY `id_publicacion` (`id_publicacion`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reaccion`
--

LOCK TABLES `reaccion` WRITE;
/*!40000 ALTER TABLE `reaccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `reaccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seguimientosemillero`
--

DROP TABLE IF EXISTS `seguimientosemillero`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seguimientosemillero` (
  `id_seguimiento` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `id_semillero` int NOT NULL,
  `fecha_seguimiento` datetime NOT NULL,
  PRIMARY KEY (`id_seguimiento`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_semillero` (`id_semillero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seguimientosemillero`
--

LOCK TABLES `seguimientosemillero` WRITE;
/*!40000 ALTER TABLE `seguimientosemillero` DISABLE KEYS */;
/*!40000 ALTER TABLE `seguimientosemillero` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semillero`
--

DROP TABLE IF EXISTS `semillero`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semillero` (
  `id_semillero` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `linea_investigacion` varchar(100) DEFAULT NULL,
  `estado` varchar(20) NOT NULL,
  `cupo_maximo` int NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  `id_facultad` int NOT NULL,
  `xp_total` int NOT NULL,
  `id_nivel_actual` int DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_semillero`),
  KEY `id_facultad` (`id_facultad`),
  KEY `id_nivel_actual` (`id_nivel_actual`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semillero`
--

LOCK TABLES `semillero` WRITE;
/*!40000 ALTER TABLE `semillero` DISABLE KEYS */;
/*!40000 ALTER TABLE `semillero` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudactualizacion`
--

DROP TABLE IF EXISTS `solicitudactualizacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudactualizacion` (
  `id_solicitud_act` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `campo_modificado` varchar(50) NOT NULL,
  `valor_anterior` varchar(255) DEFAULT NULL,
  `valor_nuevo` varchar(255) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_solicitud` datetime NOT NULL,
  `fecha_resolucion` datetime DEFAULT NULL,
  `id_admin_revisor` int DEFAULT NULL,
  `motivo_rechazo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_solicitud_act`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_admin_revisor` (`id_admin_revisor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudactualizacion`
--

LOCK TABLES `solicitudactualizacion` WRITE;
/*!40000 ALTER TABLE `solicitudactualizacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `solicitudactualizacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudliderazgo`
--

DROP TABLE IF EXISTS `solicitudliderazgo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudliderazgo` (
  `id_solicitud_lider` int NOT NULL AUTO_INCREMENT,
  `id_docente` int NOT NULL,
  `id_semillero` int NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_solicitud` datetime NOT NULL,
  `id_admin_revisor` int DEFAULT NULL,
  `fecha_resolucion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_solicitud_lider`),
  KEY `id_docente` (`id_docente`),
  KEY `id_semillero` (`id_semillero`),
  KEY `id_admin_revisor` (`id_admin_revisor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudliderazgo`
--

LOCK TABLES `solicitudliderazgo` WRITE;
/*!40000 ALTER TABLE `solicitudliderazgo` DISABLE KEYS */;
/*!40000 ALTER TABLE `solicitudliderazgo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudregistro`
--

DROP TABLE IF EXISTS `solicitudregistro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudregistro` (
  `id_solicitud` int NOT NULL AUTO_INCREMENT,
  `nombre_completo` varchar(150) NOT NULL,
  `correo_institucional` varchar(120) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `rol_solicitado` varchar(20) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_solicitud` datetime NOT NULL,
  `fecha_resolucion` datetime DEFAULT NULL,
  `id_admin_revisor` int DEFAULT NULL,
  `id_usuario_generado` int DEFAULT NULL,
  PRIMARY KEY (`id_solicitud`),
  KEY `id_admin_revisor` (`id_admin_revisor`),
  KEY `id_usuario_generado` (`id_usuario_generado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudregistro`
--

LOCK TABLES `solicitudregistro` WRITE;
/*!40000 ALTER TABLE `solicitudregistro` DISABLE KEYS */;
/*!40000 ALTER TABLE `solicitudregistro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudvinculacion`
--

DROP TABLE IF EXISTS `solicitudvinculacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudvinculacion` (
  `id_solicitud_vinc` int NOT NULL AUTO_INCREMENT,
  `id_estudiante` int NOT NULL,
  `id_semillero` int NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_solicitud` datetime NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `id_docente_revisor` int DEFAULT NULL,
  `fecha_resolucion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_solicitud_vinc`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_semillero` (`id_semillero`),
  KEY `id_docente_revisor` (`id_docente_revisor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudvinculacion`
--

LOCK TABLES `solicitudvinculacion` WRITE;
/*!40000 ALTER TABLE `solicitudvinculacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `solicitudvinculacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipologro`
--

DROP TABLE IF EXISTS `tipologro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipologro` (
  `id_tipo_logro` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `xp_otorgado` int NOT NULL,
  `limite_semanal` int DEFAULT NULL,
  PRIMARY KEY (`id_tipo_logro`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipologro`
--

LOCK TABLES `tipologro` WRITE;
/*!40000 ALTER TABLE `tipologro` DISABLE KEYS */;
/*!40000 ALTER TABLE `tipologro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre_institucional` varchar(150) NOT NULL,
  `correo_institucional` varchar(120) NOT NULL,
  `contrasena_hash` varchar(255) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `rol` varchar(20) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_registro` datetime NOT NULL,
  `foto_perfil` varchar(255) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `correo_institucional` (`correo_institucional`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;

-- Se agregan las claves foraneas despues de crear todas las tablas.
-- Las definiciones originales de las relaciones se conservan.

ALTER TABLE `administrador` ADD CONSTRAINT `administrador_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `archivo` ADD CONSTRAINT `archivo_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `archivo` ADD CONSTRAINT `archivo_ibfk_2` FOREIGN KEY (`id_publicacion`) REFERENCES `publicacion` (`id_publicacion`);

ALTER TABLE `archivo` ADD CONSTRAINT `archivo_ibfk_3` FOREIGN KEY (`id_evidencia`) REFERENCES `evidencia` (`id_evidencia`);

ALTER TABLE `archivo` ADD CONSTRAINT `archivo_ibfk_4` FOREIGN KEY (`id_avance`) REFERENCES `avanceproyecto` (`id_avance`);

ALTER TABLE `archivo` ADD CONSTRAINT `archivo_ibfk_5` FOREIGN KEY (`id_comentario`) REFERENCES `comentario` (`id_comentario`);

ALTER TABLE `avanceproyecto` ADD CONSTRAINT `avanceproyecto_ibfk_1` FOREIGN KEY (`id_proyecto`) REFERENCES `proyecto` (`id_proyecto`);

ALTER TABLE `comentario` ADD CONSTRAINT `comentario_ibfk_1` FOREIGN KEY (`id_publicacion`) REFERENCES `publicacion` (`id_publicacion`);

ALTER TABLE `comentario` ADD CONSTRAINT `comentario_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `compartido` ADD CONSTRAINT `compartido_ibfk_1` FOREIGN KEY (`id_publicacion`) REFERENCES `publicacion` (`id_publicacion`);

ALTER TABLE `compartido` ADD CONSTRAINT `compartido_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `convocatoria` ADD CONSTRAINT `convocatoria_ibfk_1` FOREIGN KEY (`id_admin_creador`) REFERENCES `administrador` (`id_usuario`);

ALTER TABLE `docentelider` ADD CONSTRAINT `docentelider_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `docentelider` ADD CONSTRAINT `docentelider_ibfk_2` FOREIGN KEY (`id_semillero_liderado`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `estudianteinvestigador` ADD CONSTRAINT `estudianteinvestigador_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `estudianteinvestigador` ADD CONSTRAINT `estudianteinvestigador_ibfk_2` FOREIGN KEY (`id_programa`) REFERENCES `programa` (`id_programa`);

ALTER TABLE `estudianteinvestigador` ADD CONSTRAINT `estudianteinvestigador_ibfk_3` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `estudianteinvestigador` ADD CONSTRAINT `estudianteinvestigador_ibfk_4` FOREIGN KEY (`id_nivel_actual`) REFERENCES `nivel` (`id_nivel`);

ALTER TABLE `evidencia` ADD CONSTRAINT `evidencia_ibfk_1` FOREIGN KEY (`id_logro`) REFERENCES `logro` (`id_logro`);

ALTER TABLE `facultad` ADD CONSTRAINT `facultad_ibfk_1` FOREIGN KEY (`id_admin_gestor`) REFERENCES `administrador` (`id_usuario`);

ALTER TABLE `historial` ADD CONSTRAINT `historial_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `historialxp` ADD CONSTRAINT `historialxp_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudianteinvestigador` (`id_usuario`);

ALTER TABLE `historialxp` ADD CONSTRAINT `historialxp_ibfk_2` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `historialxp` ADD CONSTRAINT `historialxp_ibfk_3` FOREIGN KEY (`id_logro`) REFERENCES `logro` (`id_logro`);

ALTER TABLE `inscripcionconvocatoria` ADD CONSTRAINT `inscripcionconvocatoria_ibfk_1` FOREIGN KEY (`id_convocatoria`) REFERENCES `convocatoria` (`id_convocatoria`);

ALTER TABLE `inscripcionconvocatoria` ADD CONSTRAINT `inscripcionconvocatoria_ibfk_2` FOREIGN KEY (`id_estudiante`) REFERENCES `estudianteinvestigador` (`id_usuario`);

ALTER TABLE `inscripcionconvocatoria` ADD CONSTRAINT `inscripcionconvocatoria_ibfk_3` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `insigniaotorgada` ADD CONSTRAINT `insigniaotorgada_ibfk_1` FOREIGN KEY (`id_insignia`) REFERENCES `insignia` (`id_insignia`);

ALTER TABLE `insigniaotorgada` ADD CONSTRAINT `insigniaotorgada_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `insigniaotorgada` ADD CONSTRAINT `insigniaotorgada_ibfk_3` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `logro` ADD CONSTRAINT `logro_ibfk_1` FOREIGN KEY (`id_tipo_logro`) REFERENCES `tipologro` (`id_tipo_logro`);

ALTER TABLE `logro` ADD CONSTRAINT `logro_ibfk_2` FOREIGN KEY (`id_estudiante`) REFERENCES `estudianteinvestigador` (`id_usuario`);

ALTER TABLE `logro` ADD CONSTRAINT `logro_ibfk_3` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `logro` ADD CONSTRAINT `logro_ibfk_4` FOREIGN KEY (`id_docente_registrador`) REFERENCES `docentelider` (`id_usuario`);

ALTER TABLE `logro` ADD CONSTRAINT `logro_ibfk_5` FOREIGN KEY (`id_admin_validador`) REFERENCES `administrador` (`id_usuario`);

ALTER TABLE `membresiasemillero` ADD CONSTRAINT `membresiasemillero_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudianteinvestigador` (`id_usuario`);

ALTER TABLE `membresiasemillero` ADD CONSTRAINT `membresiasemillero_ibfk_2` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `notificacion` ADD CONSTRAINT `notificacion_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `participacionevento` ADD CONSTRAINT `participacionevento_ibfk_1` FOREIGN KEY (`id_evento`) REFERENCES `evento` (`id_evento`);

ALTER TABLE `participacionevento` ADD CONSTRAINT `participacionevento_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `participacionevento` ADD CONSTRAINT `participacionevento_ibfk_3` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `programa` ADD CONSTRAINT `programa_ibfk_1` FOREIGN KEY (`id_facultad`) REFERENCES `facultad` (`id_facultad`);

ALTER TABLE `programa` ADD CONSTRAINT `programa_ibfk_2` FOREIGN KEY (`id_admin_gestor`) REFERENCES `administrador` (`id_usuario`);

ALTER TABLE `proyecto` ADD CONSTRAINT `proyecto_ibfk_1` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `publicacion` ADD CONSTRAINT `publicacion_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `publicacion` ADD CONSTRAINT `publicacion_ibfk_2` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `ranking` ADD CONSTRAINT `ranking_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudianteinvestigador` (`id_usuario`);

ALTER TABLE `ranking` ADD CONSTRAINT `ranking_ibfk_2` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `ranking` ADD CONSTRAINT `ranking_ibfk_3` FOREIGN KEY (`id_nivel`) REFERENCES `nivel` (`id_nivel`);

ALTER TABLE `reaccion` ADD CONSTRAINT `reaccion_ibfk_1` FOREIGN KEY (`id_publicacion`) REFERENCES `publicacion` (`id_publicacion`);

ALTER TABLE `reaccion` ADD CONSTRAINT `reaccion_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `seguimientosemillero` ADD CONSTRAINT `seguimientosemillero_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `seguimientosemillero` ADD CONSTRAINT `seguimientosemillero_ibfk_2` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `semillero` ADD CONSTRAINT `semillero_ibfk_1` FOREIGN KEY (`id_facultad`) REFERENCES `facultad` (`id_facultad`);

ALTER TABLE `semillero` ADD CONSTRAINT `semillero_ibfk_2` FOREIGN KEY (`id_nivel_actual`) REFERENCES `nivel` (`id_nivel`);

ALTER TABLE `solicitudactualizacion` ADD CONSTRAINT `solicitudactualizacion_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `solicitudactualizacion` ADD CONSTRAINT `solicitudactualizacion_ibfk_2` FOREIGN KEY (`id_admin_revisor`) REFERENCES `administrador` (`id_usuario`);

ALTER TABLE `solicitudliderazgo` ADD CONSTRAINT `solicitudliderazgo_ibfk_1` FOREIGN KEY (`id_docente`) REFERENCES `docentelider` (`id_usuario`);

ALTER TABLE `solicitudliderazgo` ADD CONSTRAINT `solicitudliderazgo_ibfk_2` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `solicitudliderazgo` ADD CONSTRAINT `solicitudliderazgo_ibfk_3` FOREIGN KEY (`id_admin_revisor`) REFERENCES `administrador` (`id_usuario`);

ALTER TABLE `solicitudregistro` ADD CONSTRAINT `solicitudregistro_ibfk_1` FOREIGN KEY (`id_admin_revisor`) REFERENCES `administrador` (`id_usuario`);

ALTER TABLE `solicitudregistro` ADD CONSTRAINT `solicitudregistro_ibfk_2` FOREIGN KEY (`id_usuario_generado`) REFERENCES `usuario` (`id_usuario`);

ALTER TABLE `solicitudvinculacion` ADD CONSTRAINT `solicitudvinculacion_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudianteinvestigador` (`id_usuario`);

ALTER TABLE `solicitudvinculacion` ADD CONSTRAINT `solicitudvinculacion_ibfk_2` FOREIGN KEY (`id_semillero`) REFERENCES `semillero` (`id_semillero`);

ALTER TABLE `solicitudvinculacion` ADD CONSTRAINT `solicitudvinculacion_ibfk_3` FOREIGN KEY (`id_docente_revisor`) REFERENCES `docentelider` (`id_usuario`);

/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-21 17:08:50
