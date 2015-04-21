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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player`
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*!40101 SET character_set_client = @saved_cs_client */;

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

alter table template add column description TEXT AFTER hackathon_id;
update template set description = '<ul class="services-list"><li>Ubuntu</li><li>Apache</li><li>MySQL</li<li>PHP</li></ul>' where name = 'ut' and hackathon_id = 2;
update template set description = '<ul class="services-list"><li>Ubuntu</li><li>GNome</li></ul>' where name = 'ud' and hackathon_id = 2;

-- Table: register

alter table register drop column jstrom_api ;
alter table register drop column jstrom_mgmt_portal ;
alter table register add column status INT(1) DEFAULT 0 ;
alter table register add column phone VARCHAR(11) ;
alter table register add column sex INT(1) ;
alter table register add column age INT(3) ;
alter table register add column career_type VARCHAR(16) ;
alter table register add column career VARCHAR(16) ;
alter table register add column qq VARCHAR(16) ;
alter table register add column weibo VARCHAR(16) ;
alter table register add column wechat VARCHAR(16) ;
alter table register add column address VARCHAR(64) ;
alter table register add column user_id INT(11) ;
alter table register add column update_time DATETIME ;

-- Table: hackathon

alter table hackathon drop column sponsor ;
alter table hackathon add column display_name VARCHAR(64) AFTER name ;
alter table hackathon add column registration_start_time DATETIME ;
alter table hackathon add column registration_end_time DATETIME ;
alter table hackathon add column address VARCHAR(64) ;
alter table hackathon add column description TEXT ;
alter table hackathon add column images TEXT ;

---------------------------------------- Added on 2015-04-14 ----------------------------------------

DROP TABLE IF EXISTS `SCM`;

DROP TABLE IF EXISTS `card`;

--
-- Table structure for table `azure_cloud_service`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `azure_cloud_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `label` varchar(50) DEFAULT NULL,
  `location` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `experiment_id` (`experiment_id`),
  CONSTRAINT `azure_cloud_service_ibfk_1` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azure_deployment`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `azure_deployment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `slot` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `cloud_service_id` int(11) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cloud_service_id` (`cloud_service_id`),
  KEY `experiment_id` (`experiment_id`),
  CONSTRAINT `azure_deployment_ibfk_1` FOREIGN KEY (`cloud_service_id`) REFERENCES `azure_cloud_service` (`id`) ON DELETE CASCADE,
  CONSTRAINT `azure_deployment_ibfk_2` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azure_endpoint`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `azure_endpoint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `protocol` varchar(50) DEFAULT NULL,
  `public_port` int(11) DEFAULT NULL,
  `private_port` int(11) DEFAULT NULL,
  `virtual_machine_id` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `virtual_machine_id` (`virtual_machine_id`),
  CONSTRAINT `azure_endpoint_ibfk_1` FOREIGN KEY (`virtual_machine_id`) REFERENCES `azure_virtual_machine` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azure_key`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `azure_key` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cert_url` varchar(200) DEFAULT NULL,
  `pem_url` varchar(200) DEFAULT NULL,
  `subscription_id` varchar(100) DEFAULT NULL,
  `management_host` varchar(100) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azure_log`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `azure_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operation` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `note` varchar(500) DEFAULT NULL,
  `code` int(11) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  `exec_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `experiment_id` (`experiment_id`),
  CONSTRAINT `azure_log_ibfk_1` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azure_storage_account`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `azure_storage_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `label` varchar(50) DEFAULT NULL,
  `location` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `experiment_id` (`experiment_id`),
  CONSTRAINT `azure_storage_account_ibfk_1` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azure_virtual_machine`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `azure_virtual_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `label` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `dns` varchar(50) DEFAULT NULL,
  `public_ip` varchar(50) DEFAULT NULL,
  `private_ip` varchar(50) DEFAULT NULL,
  `deployment_id` int(11) DEFAULT NULL,
  `experiment_id` int(11) DEFAULT NULL,
  `virtual_environment_id` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `last_modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `deployment_id` (`deployment_id`),
  KEY `experiment_id` (`experiment_id`),
  KEY `virtual_environment_id` (`virtual_environment_id`),
  CONSTRAINT `azure_virtual_machine_ibfk_1` FOREIGN KEY (`deployment_id`) REFERENCES `azure_deployment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `azure_virtual_machine_ibfk_2` FOREIGN KEY (`experiment_id`) REFERENCES `experiment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `azure_virtual_machine_ibfk_3` FOREIGN KEY (`virtual_environment_id`) REFERENCES `virtual_environment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

ALTER TABLE `docker_host_server` ADD CONSTRAINT `docker_host_server_ibfk_1` FOREIGN KEY (`hackathon_id`) REFERENCES `hackathon` (`id`) ON DELETE CASCADE;

ALTER TABLE `experiment` DROP FOREIGN KEY `experiment_ibfk_5`;
ALTER TABLE `experiment` ADD CONSTRAINT `experiment_ibfk_3` FOREIGN KEY (`template_id`) REFERENCES `template` (`id`) ON DELETE CASCADE;

DROP TABLE IF EXISTS `figure`;

DROP TABLE IF EXISTS `figure_data`;

DROP TABLE IF EXISTS `player`;

--
-- Table structure for table `hackathon_azure_key`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `hackathon_azure_key` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hackathon_id` int(11) DEFAULT NULL,
  `azure_key_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hackathon_id` (`hackathon_id`),
  KEY `azure_key_id` (`azure_key_id`),
  CONSTRAINT `hackathon_azure_key_ibfk_1` FOREIGN KEY (`hackathon_id`) REFERENCES `hackathon` (`id`) ON DELETE CASCADE,
  CONSTRAINT `hackathon_azure_key_ibfk_2` FOREIGN KEY (`azure_key_id`) REFERENCES `azure_key` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `role`;

DROP TABLE IF EXISTS `seed`;

UPDATE `template` SET `template`.`provider` = CASE WHEN `template`.`provider` = 'azure-vm' THEN '0' WHEN `template`.`provider` = 'docker' THEN '1' END;
ALTER TABLE `template` MODIFY `template`.`provider` int(11);

ALTER TABLE `template` ADD `virtual_environment_count` int(11);

--
-- Table structure for table `user_azure_key`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `user_azure_key` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `azure_key_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `azure_key_id` (`azure_key_id`),
  CONSTRAINT `user_azure_key_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_azure_key_ibfk_2` FOREIGN KEY (`azure_key_id`) REFERENCES `azure_key` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `user_email_j`;

DROP TABLE IF EXISTS `user_operation`;

DROP TABLE IF EXISTS `user_resource`;

DROP TABLE IF EXISTS `user_role`;

DROP TABLE IF EXISTS `user_template`;

DROP TABLE IF EXISTS `user_test_j`;

UPDATE `virtual_environment` SET `virtual_environment`.`provider` = CASE WHEN `virtual_environment`.`provider` = 'azure-vm' THEN '0' WHEN `virtual_environment`.`provider` = 'docker' THEN '1' END;
ALTER TABLE `virtual_environment` MODIFY `virtual_environment`.`provider` int(11);

UPDATE `virtual_environment` SET `virtual_environment`.`remote_provider` = '0' WHERE `virtual_environment`.`remote_provider` = 'guacamole';
ALTER TABLE `virtual_environment` MODIFY `virtual_environment`.`remote_provider` int(11);

ALTER TABLE `virtual_environment` DROP FOREIGN KEY `virtual_environment_ibfk_1`;
ALTER TABLE `virtual_environment` DROP `user_id`;

DROP TABLE IF EXISTS `vm_config`;

DROP TABLE IF EXISTS `vm_endpoint`;


----- data for online database
-- INSERT INTO `azure_key` (`id`, `pem_url`, `subscription_id`, `management_host`) VALUES (1, '/etc/open-hackathon/azure/1-31e6e137-4656-4f88-96fb-4c997b14a644.pem', '7946a60d-67b1-43f0-96f9-1c558a9d284c', 'management.core.chinacloudapi.cn');
-- INSERT INTO `hackathon_azure_key` (`id`, `hackathon_id`, `azure_key_id`) VALUES (1, 1, 1);
-- INSERT INTO `hackathon_azure_key` (`id`, `hackathon_id`, `azure_key_id`) VALUES (2, 2, 1);

---------------------------------------- Added on 2015-04-14 ----------------------------------------

alter table hackathon add column recycle_enabled int default 1 after check_register;

