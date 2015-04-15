-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: hackathon
-- ------------------------------------------------------
-- Server version	5.5.40-0ubuntu0.14.04.1

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
-- Table structure for table `SCM`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `SCM` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(20) DEFAULT NULL,
  `branch` varchar(50) DEFAULT NULL,
  `repo_name` varchar(50) DEFAULT NULL,
  `repo_url` varchar(100) DEFAULT NULL,
  `local_repo_path` varchar(100) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `experiment_id` (`experiment_id`),
  CONSTRAINT `SCM_ibfk_1` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `admin_email`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `admin_email` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `primary_email` int(11) DEFAULT NULL,
  `verified` int(11) DEFAULT NULL,
  `admin_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `admin_email_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `admin_token`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `admin_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(50) NOT NULL,
  `admin_id` int(11) DEFAULT NULL,
  `issue_date` datetime DEFAULT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `admin_token_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `admin_user`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `admin_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  `openid` varchar(100) DEFAULT NULL,
  `avatar_url` varchar(200) DEFAULT NULL,
  `access_token` varchar(100) DEFAULT NULL,
  `online` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_login_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `admin_user_hackathon_rel`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `admin_user_hackathon_rel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `admin_email` varchar(120) DEFAULT NULL,
  `role_type` int(11) DEFAULT NULL,
  `hackathon_id` int(11) DEFAULT NULL,
  `state` int(11) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `announcement`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `announcement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` varchar(200) DEFAULT NULL,
  `enabled` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apscheduler_jobs`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `apscheduler_jobs` (
  `id` varchar(191) NOT NULL,
  `next_run_time` double DEFAULT NULL,
  `job_state` blob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_apscheduler_jobs_next_run_time` (`next_run_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `card`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `card` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `skill_name` varchar(10) DEFAULT NULL,
  `skill_level` int(11) DEFAULT NULL,
  `graduated` int(11) DEFAULT NULL,
  `number` int(11) DEFAULT NULL,
  `figure_id` int(11) DEFAULT NULL,
  `player_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `figure_id` (`figure_id`),
  KEY `player_id` (`player_id`),
  CONSTRAINT `card_ibfk_1` FOREIGN KEY (`figure_id`) REFERENCES `figure` (`id`) ON DELETE CASCADE,
  CONSTRAINT `card_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `player` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `docker_container`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `docker_container` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `image` varchar(50) NOT NULL,
  `container_id` varchar(100) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `virtual_environment_id` int(11) DEFAULT NULL,
  `host_server_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `virtual_environment_id` (`virtual_environment_id`),
  KEY `host_server_id` (`host_server_id`),
  CONSTRAINT `docker_container_ibfk_1` FOREIGN KEY (`virtual_environment_id`) REFERENCES `virtual_environment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `docker_container_ibfk_2` FOREIGN KEY (`host_server_id`) REFERENCES `docker_host_server` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `docker_host_server`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `docker_host_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vm_name` varchar(100) NOT NULL,
  `hackathon_id` int(11) DEFAULT NULL,
  `public_dns` varchar(50) DEFAULT NULL,
  `public_ip` varchar(50) DEFAULT NULL,
  `public_docker_api_port` int(11) DEFAULT NULL,
  `private_ip` varchar(50) DEFAULT NULL,
  `private_docker_api_port` int(11) DEFAULT NULL,
  `container_count` int(11) NOT NULL,
  `container_max_count` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `experiment`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `experiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_heart_beat_time` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `hackathon_id` int(11) DEFAULT NULL,
  `template_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `hackathon_id` (`hackathon_id`),
  KEY `experiment_ibfk_5` (`template_id`),
  CONSTRAINT `experiment_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `experiment_ibfk_2` FOREIGN KEY (`hackathon_id`) REFERENCES `hackathon` (`id`) ON DELETE CASCADE,
  CONSTRAINT `experiment_ibfk_5` FOREIGN KEY (`template_id`) REFERENCES `template` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `figure`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `figure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(20) DEFAULT NULL,
  `avatar` varchar(120) DEFAULT NULL,
  `country` varchar(10) DEFAULT NULL,
  `init_star` int(11) DEFAULT NULL,
  `figure_type` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `figure_data`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `figure_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` varchar(20) DEFAULT NULL,
  `comment` varchar(50) DEFAULT NULL,
  `min` int(11) DEFAULT NULL,
  `max` int(11) DEFAULT NULL,
  `figure_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `figure_id` (`figure_id`),
  CONSTRAINT `figure_data_ibfk_1` FOREIGN KEY (`figure_id`) REFERENCES `figure` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hackathon`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `hackathon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `check_register` int(11) DEFAULT NULL,
  `sponsor` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `player` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `server` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `game_player_id` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `dan` int(11) DEFAULT NULL,
  `shi` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `port_binding`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `port_binding` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `port_from` int(11) NOT NULL,
  `port_to` int(11) NOT NULL,
  `binding_type` int(11) DEFAULT NULL,
  `binding_resource_id` int(11) DEFAULT NULL,
  `virtual_environment_id` int(11) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `virtual_environment_id` (`virtual_environment_id`),
  KEY `experiment_id` (`experiment_id`),
  CONSTRAINT `port_binding_ibfk_1` FOREIGN KEY (`virtual_environment_id`) REFERENCES `virtual_environment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `port_binding_ibfk_2` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=331 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `register`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `register` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `register_name` varchar(80) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `enabled` int(11) DEFAULT NULL,
  `jstrom_api` varchar(50) DEFAULT NULL,
  `jstrom_mgmt_portal` varchar(50) DEFAULT NULL,
  `hackathon_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `hackathon_id` (`hackathon_id`),
  CONSTRAINT `register_ibfk_1` FOREIGN KEY (`hackathon_id`) REFERENCES `hackathon` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `role`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seed`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `seed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `number` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `template`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `template` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `url` varchar(200) DEFAULT NULL,
  `provider` varchar(20) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `hackathon_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hackathon_id` (`hackathon_id`),
  CONSTRAINT `template_ibfk_1` FOREIGN KEY (`hackathon_id`) REFERENCES `hackathon` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  `openid` varchar(100) DEFAULT NULL,
  `avatar_url` varchar(200) DEFAULT NULL,
  `slug` varchar(50) NOT NULL,
  `access_token` varchar(100) DEFAULT NULL,
  `online` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_login_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_email`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_email` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `primary_email` int(11) DEFAULT NULL,
  `verified` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_email_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_email_j`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_email_j` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(50) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_email_j_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_test_j` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_operation`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_operation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operation` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `note` varchar(500) DEFAULT NULL,
  `exec_time` datetime DEFAULT NULL,
  `user_template_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_template_id` (`user_template_id`),
  CONSTRAINT `user_operation_ibfk_1` FOREIGN KEY (`user_template_id`) REFERENCES `user_template` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_resource`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_resource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  `user_template_id` int(11) DEFAULT NULL,
  `cloud_service_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_template_id` (`user_template_id`),
  KEY `cloud_service_id` (`cloud_service_id`),
  CONSTRAINT `user_resource_ibfk_1` FOREIGN KEY (`user_template_id`) REFERENCES `user_template` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_resource_ibfk_2` FOREIGN KEY (`cloud_service_id`) REFERENCES `user_resource` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_role`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_role_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_template`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_template` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `template_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `template_id` (`template_id`),
  CONSTRAINT `user_template_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_template_ibfk_2` FOREIGN KEY (`template_id`) REFERENCES `template` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_test_j`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_test_j` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_token`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(50) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `issue_date` datetime DEFAULT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_token_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `virtual_environment`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `virtual_environment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `remote_provider` varchar(20) DEFAULT NULL,
  `remote_paras` varchar(300) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `experiment_id` (`experiment_id`),
  CONSTRAINT `virtual_environment_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `virtual_environment_ibfk_2` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_config`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `vm_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dns` varchar(50) DEFAULT NULL,
  `public_ip` varchar(50) DEFAULT NULL,
  `private_ip` varchar(50) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  `virtual_machine_id` int(11) DEFAULT NULL,
  `remote_provider` varchar(20) DEFAULT NULL,
  `remote_paras` varchar(300) DEFAULT NULL,
  `user_template_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `virtual_machine_id` (`virtual_machine_id`),
  KEY `user_template_id` (`user_template_id`),
  CONSTRAINT `vm_config_ibfk_1` FOREIGN KEY (`virtual_machine_id`) REFERENCES `user_resource` (`id`) ON DELETE CASCADE,
  CONSTRAINT `vm_config_ibfk_2` FOREIGN KEY (`user_template_id`) REFERENCES `user_template` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_endpoint`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `vm_endpoint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `protocol` varchar(50) DEFAULT NULL,
  `public_port` int(11) DEFAULT NULL,
  `private_port` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  `cloud_service_id` int(11) DEFAULT NULL,
  `virtual_machine_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cloud_service_id` (`cloud_service_id`),
  KEY `virtual_machine_id` (`virtual_machine_id`),
  CONSTRAINT `vm_endpoint_ibfk_1` FOREIGN KEY (`cloud_service_id`) REFERENCES `user_resource` (`id`) ON DELETE CASCADE,
  CONSTRAINT `vm_endpoint_ibfk_2` FOREIGN KEY (`virtual_machine_id`) REFERENCES `user_resource` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-04-13 16:09:52

-- add a column safely
-- alter table vm_config add column dummy1 VARCHAR(40) AFTER id;
-- alter table vm_config add column dummy2 VARCHAR(40) AFTER id;
-- alter table vm_config drop column dummy1;
-- alter table vm_config drop column dummy2;

-- Table:template

-- alter table template add column description TEXT AFTER hackathon_id;
-- update template set description = '<ul class="services-list"><li>Ubuntu</li><li>Apache</li><li>MySQL</li<li>PHP</li></ul>' where name = 'ut' and hackathon_id = 2;
-- update template set description = '<ul class="services-list"><li>Ubuntu</li><li>GNome</li></ul>' where name = 'ud' and hackathon_id = 2;

-- Table: register

-- alter table register drop column jstrom_api ;
-- alter table register drop column jstrom_mgmt_portal ;
-- alter table register add column status INT(1) ;
-- alter table register add column phone VARCHAR(11) ;
-- alter table register add column sex INT(1) ;
-- alter table register add column age INT(3) ;
-- alter table register add column career VARCHAR(16) ;
-- alter table register add column qq VARCHAR(16) ;
-- alter table register add column weibo VARCHAR(16) ;
-- alter table register add column wechat VARCHAR(16) ;
-- alter table register add column address VARCHAR(64) ;
-- alter table register add column user_id INT(11) ;

-- Table: hackathon

-- alter table hackathon add column registration_start_time DATETIME ;
-- alter table hackathon add column registration_end_time DATETIME ;
-- alter table hackathon add description TEXT ;
