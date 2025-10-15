/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.28-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: mariadb    Database: events
-- ------------------------------------------------------
-- Server version	11.4.3-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'Organization Representative');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (10,1,22),(11,1,29),(12,1,30),(13,1,31),(1,1,32),(2,1,33),(3,1,34),(4,1,35),(5,1,36),(6,1,37),(7,1,38),(8,1,39),(9,1,40);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add entity',6,'add_entity'),(22,'Can change entity',6,'change_entity'),(23,'Can delete entity',6,'delete_entity'),(24,'Can view entity',6,'view_entity'),(25,'Can add user',7,'add_user'),(26,'Can change user',7,'change_user'),(27,'Can delete user',7,'delete_user'),(28,'Can view user',7,'view_user'),(29,'Can add event',8,'add_event'),(30,'Can change event',8,'change_event'),(31,'Can delete event',8,'delete_event'),(32,'Can view event',8,'view_event'),(33,'Can add author',9,'add_author'),(34,'Can change author',9,'change_author'),(35,'Can delete author',9,'delete_author'),(36,'Can view author',9,'view_author'),(37,'Can add post',10,'add_post'),(38,'Can change post',10,'change_post'),(39,'Can delete post',10,'delete_post'),(40,'Can view post',10,'view_post'),(41,'Can add page',11,'add_page'),(42,'Can change page',11,'change_page'),(43,'Can delete page',11,'delete_page'),(44,'Can view page',11,'view_page');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `blog_author`
--

DROP TABLE IF EXISTS `blog_author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `blog_author` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `image` varchar(100) NOT NULL,
  `entity_id` bigint(20) NOT NULL,
  `url` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `blog_author_entity_id_5d918eee_fk_my_profile_entity_id` (`entity_id`),
  CONSTRAINT `blog_author_entity_id_5d918eee_fk_my_profile_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `my_profile_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blog_author`
--

LOCK TABLES `blog_author` WRITE;
/*!40000 ALTER TABLE `blog_author` DISABLE KEYS */;
INSERT INTO `blog_author` VALUES (1,'Alexey Borealis','Professional astrologer.','static/img/profile/rusborn.webp',1,'example.com');
/*!40000 ALTER TABLE `blog_author` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `blog_post`
--

DROP TABLE IF EXISTS `blog_post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `blog_post` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `seo_title` varchar(100) NOT NULL,
  `seo_description` varchar(200) NOT NULL,
  `image` varchar(100) NOT NULL,
  `image_alt` varchar(100) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `content` longtext NOT NULL,
  `abstract` longtext NOT NULL,
  `date_published` datetime(6) NOT NULL,
  `date_modified` datetime(6) NOT NULL,
  `include_astrofont` tinyint(1) NOT NULL,
  `include_math` tinyint(1) NOT NULL,
  `author_id` bigint(20) NOT NULL,
  `entity_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `blog_post_author_id_dd7a8485_fk_blog_author_id` (`author_id`),
  KEY `blog_post_entity_id_f43e9ae5_fk_my_profile_entity_id` (`entity_id`),
  CONSTRAINT `blog_post_author_id_dd7a8485_fk_blog_author_id` FOREIGN KEY (`author_id`) REFERENCES `blog_author` (`id`),
  CONSTRAINT `blog_post_entity_id_f43e9ae5_fk_my_profile_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `my_profile_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blog_post`
--

LOCK TABLES `blog_post` WRITE;
/*!40000 ALTER TABLE `blog_post` DISABLE KEYS */;
INSERT INTO `blog_post` VALUES (1,'Example of Calculating Directions Using a Regular Calculator','Example of Calculating Directions Using a Regular Calculator','Not all computer programs can calculate primary directions. We will show how to perform the calculation manually.','static/img/post/directions-calc-example.jpg','Example of Calculating Directions','direction-calc-example','This article will manually calculate a primary direction from the horoscope provided [in the example of thematic forecasts](https://morinus-astrology.com/thematic-directions/). We will use only the formulas in this blog and a simple engineering calculator or Excel formulas.\r\n\r\n[toc]\r\n\r\n## Which Direction We Will Calculate\r\n\r\n<div class=\"col col-md-8 mx-auto\">\r\n<img class=\"w-100\" src=\"/static/img/page/chart1.webp\" alt=\"chart\">\r\n</div>\r\n\r\nWe will calculate the direction of <span class=\"text-astro\">tR</span> in <span class=\"text-astro\">s</span> to the cusp of the 5th house. This direction, [as we have seen](https://morinus-astrology.com/thematic-directions/), promises the native their firstborn.\r\n\r\n## Clarifying Venus\' Coordinates\r\n\r\nFirst, we will determine Venus\'s [celestial latitude](https://morinus-astrology.com/ecliptic-equator/#1-3), which is its deviation up or down from the ecliptic. Not all computer programs display this information, so we will go to the [astro.com](https://www.astro.com/swisseph/swepha_e.htm) website, in the \"20th century\" section, and choose the [year 1926](https://www.astro.com/swisseph/ae/1900/ae_1926d.pdf) in the \"with declination and latitude\" tables.\r\n\r\nIn the selected table, we find the row corresponding to April 21, the native\'s birthday. There, we will see that the celestial latitude of Venus is $\\text{lat} = 0\\text{n}5$. It means that Venus deviated by $0°5\'$ to the northern part of the celestial sphere on that day.\r\n\r\nFive arcminutes are $5/60$ or approximately $0.08$ degrees. Thus, the celestial latitude of Venus at the time of birth was $+0.08°$.\r\n\r\nCelestial longitude is the zodiacal degree of Venus starting from 0° Aries. Venus is at 13°57\' Pisces, which means it is almost 14 degrees from the beginning of Pisces, which is at 330° relative to 0° Aries. In other words, Venus is at 343°57\' of the zodiac circle. Fifty-seven arcminutes is 57/60 or 0.95 degrees. Thus, Venus\'s longitude is 343.95° relative to 0° Aries.\r\n\r\nThus, Venus has the following equatorial coordinates:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& \\lambda_P = 343.95°\\\\\r\n& \\delta_P = 0.08°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\n## Coordinates of Venus\' Sextile\r\n\r\nOur [promittor](https://morinus-astrology.com/promittors-significators/#1-1) is not Venus itself, but its sextile. Therefore, we need to find the coordinates of Venus\'s sextile on the Morinus aspect circle.\r\n\r\nFor the calculation, we will use the formula $(1)$ from the [aspect circle](https://morinus-astrology.com/circle-of-aspects/). We know the coordinates $(\\lambda_P, \\delta_P)$ of Venus itself and the magnitude of the aspect—plus 60°. The only unknowns are the maximum deviation of Venus from the ecliptic on its current path $\\delta_\\text{max}$, and whether it is moving away from or towards its point of maximum deviation.\r\n\r\nFirst, we find the maximum deviation of Venus $\\delta_\\text{max}$ on its path from the past to the nearest node. We will return to the ephemeris table for [1926](https://www.astro.com/swisseph/ae/1900/ae_1926d.pdf), which we used earlier. This time, we will move forward from April 21 and observe Venus\'s latitude until we find the point where it crosses the ecliptic.\r\n\r\nOn the next day, April 22, Venus moves into the southern hemisphere. This is evident from its latitude on the next day—0s1, meaning 0 degrees 1 minute south. Thus, somewhere between April 21 and 22, Venus crosses the ecliptic, i.e., conjuncts its south node.\r\n\r\nGreat, we have found the end of Venus\'s path of interest. Now, we need to find its beginning. For this, we will return in time to see the moment Venus last crossed the ecliptic. This moment was on the night of December 31 to January 1 of the current year.\r\n\r\nNow we scan Venus\'s entire path along the northern hemisphere—from January 1 to April 21—to find where Venus deviated most from the ecliptic to the north. The maximum elevation of Venus occurred on February 14, when its latitude was 8 degrees 21 minutes north. Since 21 minutes is 21/60 degrees, the maximum deviation of Venus can be recorded as $\\delta_\\text{max} = 8.35°.$\r\n\r\nWe also noted that Venus was at its elevation in the past, meaning it was moving away from its point of maximum elevation above the zodiac circle at the time of birth. Thus, we will use the coefficient $k = -1$ in formula $(1)$ of the [aspect circle](https://morinus-astrology.com/circle-of-aspects/). The first line of the formula looks as follows:\r\n\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\lambda\' = \\arcsin\\left(\\frac{\\sin 0.08°}{\\sin 8.35°}\\right) - 60°\r\n$$\r\n</div>\r\n\r\n**N.B.**: Please note that calculators typically work with *radians* instead of degrees.\r\n\r\nConverting degrees to radians is straightforward. You divide the degrees by 180 and multiply by $\\pi$. Here is an example of such a conversion:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n8.35° = \\frac{8.35}{180}\\pi = 0.046 \\pi = 0.1457^\\text{rad}\r\n$$\r\n</div>\r\n\r\nTo convert radians to degrees, we do the reverse—divide the number of radians by $\\pi$ and multiply by 180. For example,\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n0.1457^\\text{rad}=\\frac{0.1457}{\\pi}180 = 8.35°\r\n$$\r\n</div>\r\n\r\nTherefore, when calculating $\\sin 8.35°$ using a calculator, you need to input the number in radians, which is 0.1457 instead of 8.35.\r\n\r\nI will use degrees for convenience in this article, as it is a more straightforward form of notation. However, when working with the calculator, you must input radians.\r\n\r\nSo, returning to our formula, we see that,\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\lambda\' = \\arcsin(0.00928) - 60°\r\n$$\r\n</div>\r\n\r\nThe result of calculating $\\arcsin(0.00928)$ on the calculator is also presented in radians—this is $0.00928^\\text{rad}$, which, when converted to degrees, means $0.53°$. Thus, $\\lambda\' = -59.47°$. Since our celestial latitude turned out to be negative, we need to add 360 degrees to it to make it positive.\r\n\r\n> Rule: If you get a negative value that should be within the interval from 0 to 360 degrees, add 360° to it.\r\n\r\nSo, we found that $\\lambda\' = 300.53°.$\r\n\r\nNow, let\'s move on to the other two lines of formula $(1)$ from the [circle of aspects](https://morinus-astrology.com/circle-of-aspects/):\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& AE = \\arcsin(\\tan 0.08° / \\tan 8.35°) = 0.526° \\\\\r\n& AG = \\arctan(\\cos 8.35°\\tan 300.53°) = -59.2° \\end{align}\r\n$$\r\n</div>\r\n\r\nNow we can calculate the [ecliptic coordinates](https://morinus-astrology.com/ecliptic-equator/#1-3) of Venus\' aspect, namely:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& \\delta = \\arcsin(\\sin 300.53°\\sin 8.35°) = -0.125^\\text{rad} \\\\\r\n& \\lambda = 343.95° - (-59.2° - 0.53°) = 403.68°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nWe obtained a celestial latitude greater than 360 degrees.\r\n\r\n> Rule: if you get a value greater than 360 degrees, but it should be from 0 to 360 degrees, subtract 360° from it.\r\n\r\nAs a result, we get the ecliptic coordinates of Venus\' sextile in Taurus in the Morinus aspect circle:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& \\delta = -7.19°\\\\\r\n& \\lambda= 43.68°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nTo calculate the further direction of Venus\' sextile to the 5th house cusp, we need to express the coordinates of this sextile in the equatorial coordinate system.\r\n\r\n## Equatorial Coordinates of Venus\' Sextile\r\n\r\nTo convert the [ecliptic](https://morinus-astrology.com/ecliptic-equator/#1-3) coordinates of Venus\' sextile to [equatorial](https://morinus-astrology.com/ecliptic-equator/#1-4), we will use formula $(1)$ from the [transformation of spherical coordinates](https://morinus-astrology.com/ecliptic-equator-conversion/).\r\n\r\nWe already know the values of $\\lambda$ and $\\delta$ of our promittor; we only need the Earth\'s axial tilt angle, $\\epsilon$, which is 23.45°.\r\n\r\nSubstituting $\\lambda=43.68°$, $\\delta=-7.19°$, and $\\epsilon=23.45°$ into equation $(1)$, we get:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA = \\arctan\\left(\\frac{\\cos 23.45°\\sin 43.68° - \\sin 23.45°\\tan( -7.19°)}{\\cos 43.68°}\\right)\\\\\r\n& D = \\arcsin\\bigl(\\sin23.45°\\cos(-7.19°)\\sin 43.68° + \\cos 23.45\\sin (-7.19°)\\bigr)\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nor\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA = \\arctan\\frac{0.68}{0.72} = 0.757^\\text{rad} \\\\\r\n& D = \\arcsin(0.158) = 0.158^\\text{rad}\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\n> Rule: When dealing with the arctangent of the division of two numbers, you should use the ATAN2 function in the calculator or the Excel formula and substitute the numerator and denominator separately.\r\n\r\nNow, we can express the obtained values in degrees.\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA = 43.399° \\\\\r\n& D = 9.076°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nThese are the equatorial coordinates of Venus sextile—its right ascension $RA$ and declination $D$.\r\n\r\n## Oblique Ascension of the Ascendant\r\n\r\nTo calculate the [mundane position](https://morinus-astrology.com/ecliptic-equator/#1-6) of the significator, we will need the degree of the [oblique ascension](https://morinus-astrology.com/ecliptic-equator/#1-6) of the ascendant. The ascendant in this chart has a celestial latitude of 21°<span style=\"font-family: Astro;\">v</span>24\'. Since Capricorn starts at 270 degrees of the ecliptic, we can write that the celestial latitude of the ascendant is equal to 270° + 21° + 24/60° = 291.4°. By definition, the celestial longitude of the ascendant is zero since the cusp of the house is always in the ecliptic plane.\r\n\r\nWe need to convert the ecliptic coordinates of the ascendant—celestial latitude $\\lambda=291.4°$ and celestial longitude $\\delta=0°$—into equatorial coordinates. To do this, we will again use the familiar equation $(1)$ of the [conversion of spherical coordinates](https://morinus-astrology.com/ecliptic-equator-conversion/).\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA = \\arctan\\left(\\frac{\\cos 23.45° \\sin291.4°}{\\cos291.4°}\\right)\\\\\r\n& D = \\arcsin(\\sin 23.45°\\sin 291.4°)\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nor\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA = \\arctan\\frac{-0.85}{0.36} = -1.167^\\text{rad} \\\\\r\n& D = \\arcsin(-0.37) = -0.37^\\text{rad}\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nConverting radians to degrees, we obtain $RA = -66.86°$ and $D = -21.745°$. To eliminate the negative value of the right ascension, as usual, we will add 360 degrees:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA = 293.13° \\\\\r\n& D = -21.745°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nThese are the ascendant\'s equatorial coordinates. Knowing these coordinates, one can easily find the ascendant\'s oblique ascension. To do this, we will use the formula $(2)$ to calculate the oblique ascension. In this formula, we only need to consider the geographical coordinates of the city where the native was born.\r\n\r\nThe geographical coordinate of birth is 51° N 30\'—the native was born 51 degrees and 30 minutes north of the equator. For northern latitudes, we traditionally use the \"plus\" sign. Therefore, the geographical latitude $\\phi$ is (51 + 30/60)° with the \"plus\" sign, or $+51.5°$.\r\n\r\nNow we can use the mentioned formula $(2)$ of [calculating the oblique ascension](https://morinus-astrology.com/ascension-difference/):\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\nOA_\\text{ASC} = 293.13° - \\arcsin(\\tan 51.5° \\tan (-21.745°))\r\n$$\r\n</div>\r\n\r\nor\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\nOA_\\text{ASC} &= 293.13° - \\arcsin(-0.5) \\\\\r\n&= 293.13° - (-0.52^\\text{rad}) \\\\\r\n&= 293.13° + 30.096° = 323.23°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nWe have found the oblique ascension of the ascendant. Now, we can calculate the mundane position of the significator.\r\n\r\n## Mundane Position of the Significator\r\n\r\nThe significator is the cusp of the 5th house. Therefore, we will use the formula $(4)$ of [mundane positions calculation](https://morinus-astrology.com/regiomontanus-mundane/).\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\nMP_5 = 323.23° + 30° (5 - 1)\r\n$$\r\n</div>\r\n\r\nWe obtain a value of 443.23°, which exceeds 360°. Therefore, we subtract 360 from the obtained value. As a result, the mundane position of the 5th house cusp is 83.23°.\r\n\r\n## Arc Length of the Primary Direction\r\n\r\nNow, we can move on to calculating the arc length of the primary direction. To do this, we will use formula (1) of the [arc of the direction calculations](https://morinus-astrology.com/regiomontanus-direction/). \r\n\r\nWe will substitute the following values into this formula:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA_P = 43.399° \\\\\r\n& D_P = 9.076° \\\\\r\n& \\phi = 50.5° \\\\\r\n& OA_\\text{ASC} = 323.23° \\\\\r\n& MP_S = 83.23°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nThen we obtain the following arc length:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n\\text{Arc} & = 43.399° - \\arcsin(-0.1) - 83.23° \\\\\r\n& = 43.399° + 5.76° - 83.23° \\\\\r\n& = -34.06°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nAs usual, we add 360° to the arc to eliminate the negative value. As a result, we obtain a direction arc of 325.93°. However, there\'s a problem—this direction arc is greater than 180 degrees, and each degree roughly corresponds to one year of life. People don\'t live that long. We must find the shorter distance between the Venus sextile and the 5th house cusp.\r\n\r\nAs some ancient astrologers did, we cannot rotate the sphere in the opposite direction to obtain a +34.06° arc. This approach is meaningless—the sphere only rotates forward.\r\n\r\nWe will use the converse direction method as Morinus transmitted it. Specifically, we will temporarily consider the Venus sextile as a fixed point and direct the moving degree of the 5th house cusp towards the Venus sextile. Then, we will find a shorter path between the significator and the promittor.\r\n\r\n## Converse Direction\r\n\r\nTo use reverse direction, we need to change the promittor to the significator in formula (1) of [the direction arc calculations](https://morinus-astrology.com/regiomontanus-direction/), namely, substitute the following values:\r\n\r\n- $(RA_P, D_P)$—equatorial coordinates of the 5th house cusp\r\n- $MP_S$—mundane position of the Venus sextile\r\n\r\nThese values ​​will need to be recalculated.\r\n\r\n### Equatorial Coordinates of the Vertex of the 5th House\r\n\r\nThe 5th house cusp has the following ecliptic coordinates:\r\n\r\n- Celestial longitude $\\lambda$: 10°<span style=\"font-family: Astro;\">d</span>09\' or 10° + 60° + 9/60° =  70.15°.\r\n- Celestial latitude $\\delta$: 0°.\r\n\r\nSubstituting them into formula $(1)$ of [conversion of spherical coordinates](https://morinus-astrology.com/ecliptic-equator-conversion/), we obtain the equatorial coordinates of the 5th house cusp:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n& RA = \\arctan\\left(\\frac{\\cos 23.45°\\sin 70.15°}{\\cos 70.15°}\\right) = 68.53°\\\\\r\n& D = \\sin 23.45°\\sin70.15° = 21.98°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\n### Mundane Position of the Venus Sextile\r\n\r\nNow we will calculate the mundane position of the fixed Venus sextile using formula $(2)$ of [calculation of the mundane position](https://morinus-astrology.com/regiomontanus-mundane/), substituting into it the equatorial coordinates of the Venus sextile:\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\nMP &= \\arctan\\left(\\frac{\\sin 43.39° + \\tan 9.08°\\tan 50.5°\\cos 323.23°}{\\cos 43.39° + \\tan 9.08°\\tan 50.5°\\sin 323.23°}\\right)\\\\\r\n&=\\arctan\\left(\\frac{0.53}{0.61}\\right) = 0.714^\\text{rad} = 40.95°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\n### Arc of the Converse Direction\r\n\r\nNow we can substitute the found values into formula $(1)$ of [calculation of the arc of direction](https://morinus-astrology.com/regiomontanus-direction/):\r\n\r\n<div class=\"overflow-auto py-2\">\r\n$$\r\n\\begin{align}\r\n\\text{Arc} & = 68.53° - \\arcsin(0.108) - 40.95°\\\\\r\n& = 68.53° - 0.108^\\text{rad} - 40.95°\\\\\r\n& = 68.53° - 6.2° - 40.95°\\\\\r\n& = 21.38°\r\n\\end{align}\r\n$$\r\n</div>\r\n\r\nThis time, we obtained a positive arc length in the reverse direction without turning the celestial sphere backward. One degree of the arc of primary direction corresponds to approximately one year of life. Let\'s examine the difference we obtained:\r\n\r\n- If we had rotated the celestial sphere backward to solve the issue of reverse direction, we would have obtained an arc length of 34 degrees, corresponding to approximately 34 years of life.\r\n- However, following Morinus\'s method and simply exchanging the promittor and significator, we get a completely different arc—21 degrees. The difference is a whole decade.\r\n\r\nLet\'s verify the accuracy of the calculations according to Morinus\'s method in practice.\r\n\r\n## Verification of Obtained Results\r\n\r\nTo convert the arc of direction into years of life, we need to use the [Naibod key](https://morinus-astrology.com/primary-directions/#1-6), which is to multiply the arc of direction by 1.0147.\r\n\r\nWe find that 21.38° corresponds to 21.69 years of life or 21 years, eight months, and approximately eight days. Adding this period to the date of birth, we get the year 1947, December 30th.\r\n\r\nAs [I\'ve already noted](https://morinus-astrology.com/thematic-directions/), the direction of the promittor to the 5th house cusp (at least in female charts) more often indicates the time of conception rather than the birth of the child. Therefore, we can confidently add another nine months to this date. Then, we get the expected time of the child\'s birth in the autumn of 1948, around September-October. Indeed, the firstborn was born that autumn, November 14, 1948.\r\n\r\nIf we had followed the old method and rotated the sphere in the reverse direction when calculating converse directions, we would have arrived at a different date—August 1961. But in that year, the native did not have any children.\r\n\r\nThis example again underscores the genius of Morinus, who significantly improved the apparatus of primary directions in astrology.','Not all computer programs can calculate primary directions. In this article, we will show how to perform the calculation manually.','2024-06-03 15:37:01.261600','2024-06-08 23:43:41.769194',1,1,1,1);
/*!40000 ALTER TABLE `blog_post` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_my_profile_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_my_profile_user_id` FOREIGN KEY (`user_id`) REFERENCES `my_profile_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=315 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (276,'2025-09-28 10:35:55.833730','25','A Taste of ISAR',3,'',8,11),(277,'2025-09-28 10:36:06.531599','24','Retrograde Tales: the Good, Bad and the Ugly - Ronnie Gale Dreyer',3,'',8,11),(278,'2025-09-28 10:36:17.673383','23','Winning with a 12th House - Maurice Fernandez',3,'',8,11),(279,'2025-09-28 10:46:24.236198','22','New Book Release (Prognostic astrology)',2,'[{\"changed\": {\"fields\": [\"Date\"]}}]',8,11),(280,'2025-09-28 10:46:47.868211','21','STA Horary Astrology Certificate Course',2,'[{\"changed\": {\"fields\": [\"Date\"]}}]',8,11),(281,'2025-09-28 10:47:07.269303','20','Transforming Fixed Stars in Natal Astrology - Michael Barwick',3,'',8,11),(282,'2025-09-28 10:47:22.318574','19','Estação de Serviço: a retrogradação de Saturno em Peixes – Nuno Michaels',3,'',8,11),(283,'2025-09-28 10:47:41.401270','18','STA Horary Astrology Certificate Course (delivered live in NYC)',2,'[{\"changed\": {\"fields\": [\"Date\"]}}]',8,11),(284,'2025-09-28 10:47:57.097345','17','Astronomy for Astrologers course (online)',2,'[{\"changed\": {\"fields\": [\"Date\"]}}]',8,11),(285,'2025-09-28 10:48:09.523743','16','Malefic Planets in Astrological Magic',3,'',8,11),(286,'2025-09-28 10:48:22.980305','15','Broadcast Astrology: Demystifying the Art of Podcasting - Jen Braun',3,'',8,11),(287,'2025-09-28 10:48:53.795073','14','Conference 2024: Astral knowledge',2,'[{\"changed\": {\"fields\": [\"Date\", \"Seo title\"]}}]',8,11),(288,'2025-09-28 10:49:11.950260','13','The Meaning Of The Degrees Of The Zodiac In Astrological Interpretation - Dubravka Oberžan',3,'',8,11),(289,'2025-09-28 10:49:25.977040','12','Astrological Remediation: Handling Difficult Natal Aspects & Scary Transits',3,'',8,11),(290,'2025-09-28 10:49:43.420678','1','YouTube for Astrologers',2,'[{\"changed\": {\"fields\": [\"Date\"]}}]',8,11),(291,'2025-09-28 10:49:53.496693','2','Grounding Your Unique Brilliance',3,'',8,11),(292,'2025-09-28 10:50:28.867460','6','Astrology in Sacred Literature: Eastern',2,'[{\"changed\": {\"fields\": [\"Date\", \"Description\"]}}]',8,11),(293,'2025-09-28 10:50:49.966058','11','Persian Astrology: Legacy & Continuity',2,'[{\"changed\": {\"fields\": [\"Date\"]}}]',8,11),(294,'2025-09-28 10:51:01.381169','7','New Course in Horary Astrology',3,'',8,11),(295,'2025-09-28 10:51:32.765763','9','AA Conference 2024',2,'[{\"changed\": {\"fields\": [\"Date\", \"Seo description\", \"Description\"]}}]',8,11),(296,'2025-09-28 10:51:58.880578','10','Medical Astrology Conference 2024',2,'[{\"changed\": {\"fields\": [\"Date\", \"Seo description\", \"Description\", \"Abstract\"]}}]',8,11),(297,'2025-09-28 10:52:24.887204','8','25th FAA International Astrology Conference',2,'[{\"changed\": {\"fields\": [\"Date\", \"Description\"]}}]',8,11),(298,'2025-09-28 10:52:47.146487','5','Convergence 2025 Astrological Conference',2,'[{\"changed\": {\"fields\": [\"Date\", \"Seo title\", \"Description\"]}}]',8,11),(299,'2025-09-28 10:54:01.767297','1',' ',3,'',7,11),(300,'2025-09-28 10:54:01.774080','9','Houlding Deborah',3,'',7,11),(301,'2025-09-28 10:54:01.775811','5','McDaniel Gabriells',3,'',7,11),(302,'2025-09-28 10:54:01.777854','6','Alter Hines Martha',3,'',7,11),(303,'2025-09-28 10:54:01.779890','4','LSA Andrea',3,'',7,11),(304,'2025-09-28 10:54:01.782242','7','Houlding Deborah',3,'',7,11),(305,'2025-09-28 10:54:01.783774','8','Houlding Deborah',3,'',7,11),(306,'2025-09-28 10:54:01.785840','10','Caves Wade',3,'',7,11),(307,'2025-09-28 10:54:25.955953','2','Daniel Sowelu - Astrologer Therapist',3,'',6,11),(308,'2025-09-28 10:57:49.412951','2','My Author 1',3,'',9,11),(309,'2025-09-28 10:59:49.545120','1','Alexey Borealis',2,'[]',9,11),(310,'2025-09-28 11:00:24.606691','2','Daniel Sowelu - Astrologer Therapist',3,'',6,11),(311,'2025-09-28 11:00:35.158558','15','Wade Caves',3,'',6,11),(312,'2025-09-28 11:00:43.916818','14','Deborah Houlding',3,'',6,11),(313,'2025-09-28 11:00:59.631516','12','Skyscript',3,'',6,11),(314,'2025-09-28 11:01:08.093640','11','Living One Light',3,'',6,11);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(9,'blog','author'),(10,'blog','post'),(4,'contenttypes','contenttype'),(8,'my_events','event'),(6,'my_profile','entity'),(7,'my_profile','user'),(5,'sessions','session'),(11,'static_pages','page');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2024-06-03 12:37:35.715186'),(2,'contenttypes','0002_remove_content_type_name','2024-06-03 12:37:35.796843'),(3,'auth','0001_initial','2024-06-03 12:37:36.090906'),(4,'auth','0002_alter_permission_name_max_length','2024-06-03 12:37:36.148971'),(5,'auth','0003_alter_user_email_max_length','2024-06-03 12:37:36.161196'),(6,'auth','0004_alter_user_username_opts','2024-06-03 12:37:36.171439'),(7,'auth','0005_alter_user_last_login_null','2024-06-03 12:37:36.179884'),(8,'auth','0006_require_contenttypes_0002','2024-06-03 12:37:36.183163'),(9,'auth','0007_alter_validators_add_error_messages','2024-06-03 12:37:36.191836'),(10,'auth','0008_alter_user_username_max_length','2024-06-03 12:37:36.201560'),(11,'auth','0009_alter_user_last_name_max_length','2024-06-03 12:37:36.213323'),(12,'auth','0010_alter_group_name_max_length','2024-06-03 12:37:36.249079'),(13,'auth','0011_update_proxy_permissions','2024-06-03 12:37:36.256924'),(14,'auth','0012_alter_user_first_name_max_length','2024-06-03 12:37:36.263523'),(15,'my_profile','0001_initial','2024-06-03 12:37:36.705718'),(16,'admin','0001_initial','2024-06-03 12:37:36.855903'),(17,'admin','0002_logentry_remove_auto_add','2024-06-03 12:37:36.874166'),(18,'admin','0003_logentry_add_action_flag_choices','2024-06-03 12:37:36.885394'),(19,'blog','0001_initial','2024-06-03 12:37:37.003067'),(20,'blog','0002_initial','2024-06-03 12:37:37.131354'),(21,'my_events','0001_initial','2024-06-03 12:37:37.156982'),(22,'my_events','0002_initial','2024-06-03 12:37:37.221693'),(23,'sessions','0001_initial','2024-06-03 12:37:37.281464'),(24,'blog','0003_alter_author_image','2024-06-03 15:58:31.810722'),(25,'my_profile','0002_remove_user_photo','2024-06-03 15:58:31.852752'),(26,'my_profile','0003_rename_logo_entity_image','2024-06-03 16:08:46.410063'),(27,'blog','0004_remove_author_slug_author_url','2024-06-03 18:57:28.026986'),(28,'my_events','0003_event_abstract_event_title','2024-06-03 19:07:37.270590'),(29,'static_pages','0001_initial','2024-06-05 10:02:10.463012'),(30,'my_events','0003_event_timezone','2024-06-06 07:48:08.793901'),(31,'my_events','0004_event_registration_url','2024-06-07 14:24:53.180666'),(32,'my_events','0005_event_seo_description_event_seo_title','2024-06-08 08:01:22.902834'),(33,'my_events','0006_event_duration_event_format','2024-06-18 04:51:58.207078'),(34,'my_events','0007_alter_event_format','2024-06-18 04:56:02.393114'),(35,'my_events','0008_event_audience','2024-06-21 08:02:01.654559'),(36,'my_events','0009_alter_event_audience','2024-06-21 08:50:48.360477');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('btpbcmau13fej4rhzo4ifpq697wkjfwr','.eJxVjEEOwiAQRe_C2pCBghSX7j0DGQZGqgaS0q6Md7dNutDtf-_9twi4LiWsPc9hSuIirDj9bhHpmesO0gPrvUlqdZmnKHdFHrTLW0v5dT3cv4OCvWy1YWvBeT2g8ToTawfI5JH1CMDOpahpIMUj-GgVRbf5g-LkOJt8BhSfL-KsODY:1sPiuu:2y1Evz9iLr5NqjnqE77sZwhXwxaxKeWRU9tnjA1SP64','2024-07-19 13:24:00.945976'),('cfhn2bzaeao99dp0qkzfo50g1cglfsmn','.eJxVjEEOwiAQRe_C2hCmUxBcuvcMZOgMUjU0Ke3KeHdD0oVu_3vvv1WkfStxb7LGmdVFgTr9bommp9QO-EH1vuhpqds6J90VfdCmbwvL63q4fweFWum1ZUqCMDCZEcE7AhBhF7wz6MOYMZ-TRZCQ_YDOAlmxLhlgRAKP6vMF3Yw3Nw:1sE6xR:4Hn_itbGKugKb75iNf5aavdsD2ZZhwRYu56J7F0DjCM','2024-06-17 12:38:37.743340'),('etg2h8u7q1shbkakkcrj2xvlsp2l4dg6','.eJxVjEEOwiAQRe_C2hCmUxBcuvcMZOgMUjU0Ke3KeHdD0oVu_3vvv1WkfStxb7LGmdVFgTr9bommp9QO-EH1vuhpqds6J90VfdCmbwvL63q4fweFWum1ZUqCMDCZEcE7AhBhF7wz6MOYMZ-TRZCQ_YDOAlmxLhlgRAKP6vMF3Yw3Nw:1sGG94:T9efVGVieUq420smT5YRiIBBEyj5-WHkAM2NpXCM49c','2024-06-23 10:51:30.046852'),('gprvcrcyhwkjeem6l8e8a73y2j4o24p2','.eJxVjEEOwiAQRe_C2pCBghSX7j0DGQZGqgaS0q6Md7dNutDtf-_9twi4LiWsPc9hSuIirDj9bhHpmesO0gPrvUlqdZmnKHdFHrTLW0v5dT3cv4OCvWy1YWvBeT2g8ToTawfI5JH1CMDOpahpIMUj-GgVRbf5g-LkOJt8BhSfL-KsODY:1sI8cN:ijOydiReCQamJgX9mvzBloWEo1WLUs5-pNEiYXujtKU','2024-06-28 15:13:31.103841'),('k4dezy2p8qswv2477wq2yvh81vdsunnk','.eJxVjEEOwiAQRe_C2hAoMAWX7j0DYWZAqoYmpV0Z765NutDtf-_9l4hpW2vcel7ixOIsrDj9bpjokdsO-J7abZY0t3WZUO6KPGiX15nz83K4fwc19fqtNY5AekBNKgAAg7bJWTViKcRDoGSCUuSMs4ghex8QCgAykmGD3or3B9qSOAM:1sJHmh:VB3h1n3l8zuRKgw2DS3ezGeaDIxORgoD97Z88gvOVIE','2024-07-01 19:12:55.206711'),('krwa3e1zezxrstzvjvw8tmib8u8hjpfs','.eJxVjEEOwiAQRe_C2hCmtAy4dO8ZyDBMpWpoUtqV8e7apAvd_vfef6lI21ri1mSJU1ZnBaBOv2MifkjdSb5Tvc2a57ouU9K7og_a9HXO8rwc7t9BoVa-NVoE4533A3TWEUjog0fKYy9og7OI7A1yl8Al68RYYnHGwCgZzQCs3h_H4Tbr:1v2p5s:2kjU9a57yTXpJRUXLpTPmBPlrRYVwk6BlVFiZ9y7_Dw','2025-10-12 10:57:28.053182'),('n69h5kje1d63jno8cphjej0u2ihg83of','.eJxVjMsOwiAQRf-FtSEgjwGX7vsNZIBBqgaS0q6M_65NutDtPefcFwu4rTVsg5YwZ3ZhwE6_W8T0oLaDfMd26zz1ti5z5LvCDzr41DM9r4f7d1Bx1G-NzijrLQiFWVpyLktSSTlRDOkIJAQm68UZilNaZiSTDFGxElL0ETR7fwDWaTfj:1sJGmK:OaNY7XGDZ9f0l0fjaVSHMC7OCPyANIcyJ4qF-9CeTK0','2024-07-01 18:08:28.116786'),('ofpprs4t9xwh0jg33uvtzevnk0odyoqm','.eJxVjDsOwjAQBe_iGln-rRNT0nMGa71e4wBypDipEHeHSCmgfTPzXiLitta4dV7ilMVZGHH63RLSg9sO8h3bbZY0t3WZktwVedAur3Pm5-Vw_w4q9vqtLQNzcJDJg4eCNoeixxEDBXCBkjbFKO3JGa2UKp4JeRgSoNUEyljx_gDl2jec:1sFugs:oJssgxFUTdWrZ9mTmj3CaWEBOX9q9GsCNGv8rLvBEps','2024-06-22 11:56:58.223033'),('tcpibwbtj9qvij24ugndhaapqwuut6zo','.eJxVjDsOwjAQBe_iGln-rRNT0nMGa71e4wBypDipEHeHSCmgfTPzXiLitta4dV7ilMVZGHH63RLSg9sO8h3bbZY0t3WZktwVedAur3Pm5-Vw_w4q9vqtLQNzcJDJg4eCNoeixxEDBXCBkjbFKO3JGa2UKp4JeRgSoNUEyljx_gDl2jec:1sEDJn:5UwoYavMmgnKQmsYC-6izFEO80EjscgytmSwWrtYml0','2024-06-17 19:26:07.738413'),('urx2mjkqjgd8hgwxu4y721q03ww4kkij','.eJxVjEEOwiAQRe_C2pBhbCl16d4zkJkBpGogKe3KeHdD0oVu_3vvv5Wnfct-b3H1S1AX5dTpd2OSZywdhAeVe9VSy7YurLuiD9r0rYb4uh7u30GmlnsNyDijYJA4GsNuCNZRTCnaxCAyMrNBJpqQzBkGACszISCliQyT-nwBDas46g:1sJKsG:g0Nk_r008PhCzGOKr_oUAgB80-DaLOb9mbh5FpIwdJM','2024-07-01 22:30:52.179981'),('usgyf6ag2zbev2kptwzz7q30ei3ijg5x','.eJxVjEEOwiAQRe_C2hCmUxBcuvcMZOgMUjU0Ke3KeHdD0oVu_3vvv1WkfStxb7LGmdVFgTr9bommp9QO-EH1vuhpqds6J90VfdCmbwvL63q4fweFWum1ZUqCMDCZEcE7AhBhF7wz6MOYMZ-TRZCQ_YDOAlmxLhlgRAKP6vMF3Yw3Nw:1sJFb2:DAPdZ71QoBRzSQzFQ4S-U47T3tHkPRYQGBCezufccjo','2024-07-01 16:52:44.951165'),('utnnhr9cfsz6uq8ocgedznwuoliqbh1i','.eJxVjEEOwiAQRe_C2hCmUxBcuvcMZOgMUjU0Ke3KeHdD0oVu_3vvv1WkfStxb7LGmdVFgTr9bommp9QO-EH1vuhpqds6J90VfdCmbwvL63q4fweFWum1ZUqCMDCZEcE7AhBhF7wz6MOYMZ-TRZCQ_YDOAlmxLhlgRAKP6vMF3Yw3Nw:1sEmrY:b4GqUA4cFb58Uz7Ynz5XGla-HwoK9fj6c7MMaTFCfL4','2024-06-19 09:23:20.685202'),('wf206ufnqeqqlxzugufqp0vqko2cuhom','.eJxVjDsOwjAQBe_iGln-rRNT0nMGa71e4wBypDipEHeHSCmgfTPzXiLitta4dV7ilMVZGHH63RLSg9sO8h3bbZY0t3WZktwVedAur3Pm5-Vw_w4q9vqtLQNzcJDJg4eCNoeixxEDBXCBkjbFKO3JGa2UKp4JeRgSoNUEyljx_gDl2jec:1sEnlM:8sP5k_8H5HoIEYOpPB5emgjP41bBcicI7ur5SNDKeSg','2024-06-19 10:21:00.733758');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `my_events_event`
--

DROP TABLE IF EXISTS `my_events_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_events_event` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date` datetime(6) NOT NULL,
  `type` varchar(100) NOT NULL,
  `image` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `entity_id` bigint(20) NOT NULL,
  `abstract` longtext NOT NULL,
  `title` varchar(100) NOT NULL,
  `timezone` varchar(32) NOT NULL,
  `registration_url` varchar(200) NOT NULL,
  `seo_description` varchar(200) NOT NULL,
  `seo_title` varchar(100) NOT NULL,
  `duration` varchar(50) NOT NULL,
  `format` varchar(50) NOT NULL,
  `audience` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `my_events_event_entity_id_1cc44bb5_fk_my_profile_entity_id` (`entity_id`),
  CONSTRAINT `my_events_event_entity_id_1cc44bb5_fk_my_profile_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `my_profile_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `my_events_event`
--

LOCK TABLES `my_events_event` WRITE;
/*!40000 ALTER TABLE `my_events_event` DISABLE KEYS */;
INSERT INTO `my_events_event` VALUES (1,'2034-06-16 19:03:07.000000','course','static/img/event/event2.jpg','Video astrology is a skill of its own. This class with Nadiya Shah is ideal if you are considering offering videos or engaging social media as part of your practice, if you are new to YouTube or social media, or you want the support, ideas, and inspiration to reignite your established channel or platform.',3,'This class with Nadiya Shah is ideal if you are considering offering videos or engaging social media.','YouTube for Astrologers','+00:00','https://store.keplercollege.org/product/youtube-for-astrologers-2/','This class with is ideal if you are considering offering videos or engaging social media as part of your practice','YouTube for Astrologers - event by Kepler Colledge','oneday','online','any'),(5,'2035-03-07 12:00:00.000000','conference','static/img/event/Convergence2025.jpg','This is a LIVE in-person conference in Orlando, Florida. No matter your astrological experience or knowledge level, you\'re warmly invited to the conference, where you\'re bound to find enjoyment. Each lecture promises to deliver fresh insights and discoveries, enriching your understanding of astrology.\r\n\r\nLet\'s embrace with open hearts and curious minds as we embark on crafting a tapestry of knowledge. Let\'s honor the unique threads of each tradition, fostering a culture of mutual respect as we journey together.\r\n\r\nCosmic Patterns Convergence, an in person event March 7 - 9, 2035, Florida, USA',4,'This is a LIVE in-person conference in Orlando, Florida. No matter your astrological experience or knowledge level, you\'re warmly invited','Convergence 2025 Astrological Conference','-05:00','https://cosmicpatternsconference.com/','No matter your astrological experience or knowledge level, you\'re warmly invited to the conference, where you\'re bound to find enjoyment.','Convergence 2035 Astrological Conference','multiday','in_person','any'),(6,'2034-07-06 08:00:00.000000','webinar','static/img/event/Astrology_in_Sacred_Literature1.jpg','Follow astrology down the sacred paths in the written word. The greatest collection of works on the soul and, surprisingly, its intersection with astrological concepts, come from traditional religions.\r\n\r\nExplore Hinduism via The Rig Veda, Upanishads, Bhagavad-Gita, and Ramayana; Buddhism via The Wheel of Life (story of Siddhartha), and Dhammapada; Confucianism via the Analects, I-Ching, and Tao Te-Ching (an off-shoot of Confucianism).\r\n\r\n- Instructor: Carol Tebbs\r\n- H106 (5 weeks) – Summer 2033-34\r\n- Class begins July 6, 2034\r\n- Advance pricing until June 22, 2034\r\n\r\n*NOTE*: If this is your first academic course with Kepler College or you have not paid the one-time registration fee ($40) in the past, please add this to your order. This fee payment is required for all academic students.\r\n\r\nThe one-time Registration fee is a separate store item found as the last item in each term grouping.\r\n\r\nThis course is taught in English. Proficiency in English is required for all students.',3,'In Carol Tebbs\' course, \"Astrology in Sacred Literature: Eastern\", you\'ll follow astrology down the sacred paths in the written word.','Astrology in Sacred Literature: Eastern','-08:00','https://store.keplercollege.org/product/astrology-in-sacred-literature-eastern/','Explore Hinduism via The Rig Veda, Upanishads, Bhagavad-Gita, and Ramayana; Buddhism via The Wheel of Life, and Dhammapada','Event by Kepler Colledge - Astrology in Sacred Literature','oneday','online','any'),(8,'2035-01-16 08:00:00.000000','conference','static/img/event/conf-faa.jpg','Thursday 16th January to Monday 20th January 2035\r\n\r\n- Venue: Novotel Hotel Surfers Paradise\r\n- Theme: Yesterday Today Tomorrow\r\n\r\n## CELEBRATING THE 30TH ANNIVERSARY OF THE INCORPORATION OF THE FAA!\r\n\r\nThe theme for the 2035 FAA Conference is Yesterday Today Tomorrow\r\n\r\nYesterday, Today and Tomorrow plants bring colour to a tropical garden during the late winter months when few other plants are in bloom. It’s flowers release a delightful fragrance both day and night. The pretty spring flowers start deep purple, then fade to lilac and white as they mature.\r\n\r\nWe are thrilled to present a richly diverse lineup of lectures, spanning classical, psychological, evolutionary, and even magical themes – all under the overarching theme of Yesterday Today Tomorrow! Our schedule features speakers who will take you on an intellectually stimulating journey, challenging your perspectives, expanding your horizons, and inviting exploration of new ideas and concepts.',5,'Join the FAA International Conference in Queensland, Australia. Discover cutting-edge astrological insights and connect with global experts.','25th FAA International Astrology Conference','+10:00','https://faainc.org.au/2025-faa-conference/','Join the FAA International Conference in Queensland, Australia. Discover cutting-edge astrological insights and connect with global experts. Don\'t miss out!','25th FAA International Astrology Conference','multiday','in_person','any'),(9,'2034-08-28 08:00:00.000000','conference','static/img/event/aa-conf.jpg','The theme of the 2034 conference is ‘Diverse Perspectives: All Themes Considered’ as we celebrate the forthcoming and final ingress of Pluto into Aquarius.\r\n\r\nThere will be a residential conference as well as via Zoom Online from Wednesday 28 August to Sunday 01 September 2034. We will also be offering a tour to the National Space Centre on Thursday 29 August for those who wish to join the conference earlier.',6,'There will be a residential conference as well as via Zoom Online. We will also be offering a tour to the National Space Centre on Thursday 29 August','AA Conference 2024','+00:00','https://www.astrologicalassociation.com/conference-2024','56th Annual Conference ‘Diverse Perspectives; All Themes Considered’ 28 August – 1 September 2034','56th Annual Conference - Astrologica Association','multiday','in_person','any'),(10,'2034-10-04 08:00:00.000000','conference','static/img/event/astro-med-conf24.jpg','Join us for a unique event hosted by the American Federation of Astrologers! From October 4-6, 2034, the Medical Astrology Conference will take place at the Embassy Suites in Tempe, Arizona, featuring leading experts sharing their knowledge and expertise.\r\n\r\nEnjoy inspiring lectures from renowned specialists: Lynn Koiner, Diane Cramer, Kathryn Silverton, Dr. Will Morris, and Kathy Allan. Gain invaluable insights into medical astrology and apply your newfound knowledge in practice.\r\n\r\nRegistration is now open! Don’t miss the opportunity to take advantage of early bird discounts and special offers for AFA members. Secure your spot today and enjoy comfortable accommodation at the Embassy Suites with special rates.\r\n\r\nRegister online at www.astrologers.com or send your payment to: AFA, 6535 S. Rural Rd, Tempe, AZ 85283. For more information, call 480-838-1751 or toll-free at 888-301-7630, or email us at info@astrologers.com.\r\n\r\nCome a day early for the special pre-conference class on chart calculations, free on Friday from 9:00 am to 12:00 pm, taught by Demetra George and Omari Martin.',7,'Join us for a unique event hosted by the American Federation of Astrologers! From October 4-6, 2034, the Medical Astrology Conference.','Medical Astrology Conference 2024','-07:00','https://www.astrologers.com/2024-conference/','Join the Medical Astrology Conference 2034 in Tempe, AZ, October 4-6, with top experts. Early bird registration now open','Medical Astrology Conference - American Federation of Astrologers','multiday','in_person','any'),(11,'2034-07-06 19:00:00.000000','webinar','static/img/event/persian-astrology.jpg','In this webinar we will present Persian astrology, discussing its history and introducing its system. We will highlight its metaphysical context, key developments, and influential figures who have shaped its course as well as current practices and resources.',3,'In this webinar we will present Persian astrology, discussing its history and introducing its system.','Persian Astrology: Legacy & Continuity','+02:00','https://keplercollege-org.zoom.us/webinar/register/1517172121974/WN_kR0KrrhjTuub4IKzVFAnsg#/registration','In this webinar we will present Persian astrology, discussing its history and introducing its system.','Persian Astrology: Legacy & Continuity','oneday','online','advanced'),(14,'2034-09-13 10:00:00.000000','conference','static/img/event/astral-knowledge.jpg','**Astral Knowledge: Transmissions, technologies, & texts** is the theme for this year\'s conference.\r\n\r\nSome highlights from the text are below. \r\n\r\n>\"For Hermes, that wily devil, curiosity is King. The mark of their children is the eagerness of their curio, which darts about, much like their progenitor. We find it in the eye of the stellar witch, the hands of the celestial wizard, the voice of the seraphic conjurer, the perception of the astral diviner, and the intellect of the heavenly sage. Their powers are keen, skilled, and erudite when cultivated. For if curiosity is King, its cultivation is Key.\r\n\r\n>\"Astral knowledge is that of celestial divination, omen, prognostication, astrology, astronomy, and magic, as well as their many applications. Such knowledge incorporates particular theoretical and practical understanding. It is acquired through a mix of specific learning and experience.\r\n[...]\r\n\r\n>\"For those among us, curious to the above and about, the dance of heaven and earth is at once myriad, particular, complex, harmonised, and mysterious and it constitutes various knowledge.\r\n\"Our knowledge is astral and it is celestially formed, informed, and transformed. Now as before, there is much to be done and much to be shared. There are stellar litanies to write, heavenly orations to compose, astral figures to draw, empyrean data to tabulate, and celestial curios to cultivate.\r\n\r\nYou are invited to join us in this fourth Astro Magia as we survey, inspect, search, and traverse with fresh eyes ASTRAL KNOWLEDGE: TRANSMISSIONS, TECHNOLOGIES, & TEXTS.',10,'You are invited to join the fourth Astro Magia Conference this September to inspect, search, and traverse with fresh eyes ASTRAL KNOWLEDGE','Conference 2024: Astral knowledge','+00:00','https://astromagia.org/','Astral knowledge is that of celestial divination, omen, prognostication, astrology, astronomy, and magic, as well as their many applications','Event by Astro Magia - Conference 2034: Astral knowledge','multiday','in_person','any'),(17,'2035-01-12 12:00:00.000000','course','static/img/event/Screenshot_2024-06-17_at_2.07.32PM.png','There can be nothing more valuable to the dedicated astrologer than a firm grounding in foundational astronomy. In this course, you will learn how we measure motion and position in the heavens, build proficiency in chart calculation, and be invited to consider the philosophical implications made when dividing the sky using this technique vs that. Instructional elements of this course open a door to the past, affording glimpses into the lives, contributions, and methods of astronomy’s master disciples like Ptolemy (2nd c.), Al-Biruni (11th c.), Copernicus (16th c.), and Kepler (17th c.). By the end of this course, you will be able to calculate a chart by hand with nothing more than an ephemeris and a table of houses and participate in informed astronomical discussion.',13,'Learn astronomical precepts in a visual and collaborative environment. Perfect for those who want to learn how to calculate a chart by hand.','Astronomy for Astrologers course (online)','-04:00','https://sta.co/astronomy/A007.php','Master chart calculation and dive into astrology\'s rich astronomical foundations in this 7-week online course.','Astronomy for Astrologers course (online)','multiday','online','advanced'),(18,'2034-08-03 10:00:00.000000','course','static/img/event/livehorary.jpg','The STA’s uniquely structured horary course is suitable for astrologers with a secure grasp of basic astrological principles and experience of drawing up and interpreting charts. Previous experience in horary is not necessary: we provide a full theoretical overview and highlight the most useful and reliable principles of judgement. We show how to draw out the meaning of the chart in the most effective manner and how to prepare for the sensitive issues that arise within a horary consultation. The course offers a practitioner level of accreditation, and by the end of it any astrologer who is delivering a professional astrology service will be able to include horary within their services.\r\n\r\nThis course is offered live in New York City, with some online components.',13,'Learn the art of answering life\'s questions with horary. Earn certification and practical experience from seasoned tutors in this immersive program.','STA Horary Astrology Certificate Course (delivered live in NYC)','-04:00','https://sta.co/horary/H58_AUG24.php','Learn traditional horary astrology from seasoned instructors. Gain hands-on experience interpreting real client charts in this comprehensive certification course.','Horary astrology course (live in NYC)','multiday','in_person','any'),(21,'2034-10-05 16:00:00.000000','course','static/img/event/online.jpg','The STA’s uniquely structured horary course is suitable for astrologers with a secure grasp of basic astrological principles and experience of drawing up and interpreting charts. Previous experience in horary is not necessary: we provide a full theoretical overview and highlight the most useful and reliable principles of judgement. We show how to draw out the meaning of the chart in the most effective manner and how to prepare for the sensitive issues that arise within a horary consultation. The course offers a practitioner level of accreditation, and by the end of it any astrologer who is delivering a professional astrology service will be able to include horary within their services.\r\n\r\nThis course is offered online.',13,'Learn the art of answering life\'s questions with horary. Earn certification and practical experience from seasoned tutors in this immersive program.','STA Horary Astrology Certificate Course','+00:00','https://sta.co/horary/H60_OCT24.php','Learn traditional horary astrology from seasoned instructors. Gain hands-on experience interpreting real client charts in this comprehensive certification course.','Horary astrology certification course','multiday','online','any'),(22,'2034-07-07 00:00:00.000000','other','static/img/event/book-img.jpg','Astrology has been developed and designed as a predictive\r\ndiscipline. Unfortunately, in recent years, it has taken on the role of\r\na pseudo-psychological science. Surprisingly, many modern\r\nastrologers have become so fascinated with trendy esoteric beliefs\r\nthat they have stopped accepting the idea of accurate astrological\r\npredictions. Nevertheless, astrology enables predicting\r\nprecise dates and details of events. Soon, you will see for yourself.\r\n\r\nThis book is written in the form of a textbook, guiding you step-by-\r\nstep from beginner to expert in predictions. It will teach you to\r\nmake independent and accurate forecasts, explaining how to use\r\nyour knowledge about the future.\r\n\r\nAstrology thrived as a scientific discipline in European universities\r\nin the 17th century. So, the works of renowned astrologers of that\r\ntime—William Lilly and Jean-Baptiste Morin de Villefranche, whose\r\nprecise predictions earned them lasting fame, lie at the basis of this\r\nbook.\r\n\r\n## Special Offer\r\n\r\n**In connection with the book\'s release on July 8, 2024, it will be available on Amazon Kindle for free in exchange for your review after reading it. Click \"register now\" to preview the book and download a calendar reminder with the link to read the book for free on July 8th.**',1,'This comprehensive textbook takes you on a step-by-step journey from beginner to expert in predictive astrology.','New Book Release (Prognostic astrology)','-07:00','https://morinus-astrology.com/predictive-astrology-book/','Discover new textbook - a comprehensive guide to master predictive techniques. Learn with real examples and exercises.','Mysteries of Medieval Astrology: Powerful Predictive Tools','oneday','online','any');
/*!40000 ALTER TABLE `my_events_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `my_profile_entity`
--

DROP TABLE IF EXISTS `my_profile_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_profile_entity` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `website` varchar(200) NOT NULL,
  `image` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `my_profile_entity`
--

LOCK TABLES `my_profile_entity` WRITE;
/*!40000 ALTER TABLE `my_profile_entity` DISABLE KEYS */;
INSERT INTO `my_profile_entity` VALUES (1,'Morinus\' School of Astrology','https://morinus-astrology.com/en/','static/img/logo/morinus-logo-white.png'),(3,'Kepler Colledge','https://www.keplercollege.org/','static/img/logo/kepler-colledge.png'),(4,'Cosmic Patterns Software','https://astrosoftware.com/','static/img/logo/cpsealhead.gif'),(5,'Federation of Australian Astrologers','https://www.faainc.org.au/','static/img/logo/faaInc-logo.png'),(6,'Astrological Association of Great Britain','https://www.astrologicalassociation.com/','static/img/logo/aagb.jpg'),(7,'American Federation of Astrologers','https://www.astrologers.com/','static/img/logo/afa-logo.jpg'),(8,'London School of Astrology','https://www.londonschoolofastrology.com/','static/img/logo/lsa-logo.png'),(9,'ISAR','https://isarastrology.com/','static/img/logo/isar-logo.png'),(10,'Astro Magia','astromagia.org','static/img/logo/astro-magia-logo.jpg'),(13,'School of Traditional Astrology (STA)','https://sta.co/','static/img/logo/sta-logo.png');
/*!40000 ALTER TABLE `my_profile_entity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `my_profile_user`
--

DROP TABLE IF EXISTS `my_profile_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_profile_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) NOT NULL,
  `entity_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `my_profile_user_entity_id_bd22d11b_fk_my_profile_entity_id` (`entity_id`),
  CONSTRAINT `my_profile_user_entity_id_bd22d11b_fk_my_profile_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `my_profile_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `my_profile_user`
--

LOCK TABLES `my_profile_user` WRITE;
/*!40000 ALTER TABLE `my_profile_user` DISABLE KEYS */;
INSERT INTO `my_profile_user` VALUES (11,'pbkdf2_sha256$600000$H9S6eAc0OMAOz4t44swNuR$xWNxfi4yvXZFImffooAxtPw7bc29reDa8t62+dPOChU=','2025-09-28 10:57:28.051183',1,'demouser','','',1,1,'2025-09-28 10:34:46.894844','demo@demo.user',NULL);
/*!40000 ALTER TABLE `my_profile_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `my_profile_user_groups`
--

DROP TABLE IF EXISTS `my_profile_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_profile_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `my_profile_user_groups_user_id_group_id_474fae91_uniq` (`user_id`,`group_id`),
  KEY `my_profile_user_groups_group_id_8aeb9705_fk_auth_group_id` (`group_id`),
  CONSTRAINT `my_profile_user_groups_group_id_8aeb9705_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `my_profile_user_groups_user_id_a95656d0_fk_my_profile_user_id` FOREIGN KEY (`user_id`) REFERENCES `my_profile_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `my_profile_user_groups`
--

LOCK TABLES `my_profile_user_groups` WRITE;
/*!40000 ALTER TABLE `my_profile_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `my_profile_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `my_profile_user_user_permissions`
--

DROP TABLE IF EXISTS `my_profile_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_profile_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `my_profile_user_user_per_user_id_permission_id_e99ddc74_uniq` (`user_id`,`permission_id`),
  KEY `my_profile_user_user_permission_id_cc9b89b0_fk_auth_perm` (`permission_id`),
  CONSTRAINT `my_profile_user_user_permission_id_cc9b89b0_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `my_profile_user_user_user_id_b17f5351_fk_my_profil` FOREIGN KEY (`user_id`) REFERENCES `my_profile_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `my_profile_user_user_permissions`
--

LOCK TABLES `my_profile_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `my_profile_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `my_profile_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `static_pages_page`
--

DROP TABLE IF EXISTS `static_pages_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `static_pages_page` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `seo_title` varchar(100) NOT NULL,
  `seo_description` varchar(200) NOT NULL,
  `image` varchar(100) NOT NULL,
  `image_alt` varchar(100) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `content` longtext NOT NULL,
  `date_published` datetime(6) NOT NULL,
  `date_modified` datetime(6) NOT NULL,
  `include_astrofont` tinyint(1) NOT NULL,
  `include_math` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `static_pages_page`
--

LOCK TABLES `static_pages_page` WRITE;
/*!40000 ALTER TABLE `static_pages_page` DISABLE KEYS */;
INSERT INTO `static_pages_page` VALUES (1,'Astrological Events Worldwide','Astrological Events Worldwide - A Global Hub for All Events','All events in one place! Conferences, webinars, courses, and more on Astrological Events Worldwide. Stay updated','static/img/page/killing-transit.jpg','Astrological Events Worldwide','main','Whatever content','2024-06-05 10:16:45.040152','2024-06-08 08:27:52.808967',0,0),(2,'Astrology Blog','Articles on astrology published by professional astrologers','Explore expert insights with articles on astrology by professional astrologers. Get forecasts, trends, and guidance.','static/img/page/blog-share.jpg','lala','blog','Whatever text','2024-06-07 18:00:02.948121','2024-06-08 08:31:32.471788',0,0),(3,'About AstroHub','About Global Astrological Events Aggregator','Discover and share astrological events worldwide. Join us and connect with astrologers from around the globe!','static/img/page/about.jpg','About AstroHub','about','<div class=\"container py-5 my-5 post\">\r\n  <div class=\"row\">\r\n    <div class=\"col col-md-8 mx-auto\">\r\n      <h1 class=\"font-title\">About Us</h1>\r\n      <p>The astrological community has grown tremendously over the years. With countless online events happening worldwide, there has been a pressing need for a unified platform where astrologers from around the globe can announce their events and invite participants from afar. Typically, astrologers share their events within local social media groups, limiting their reach.</p>\r\n      <p>We are thrilled to introduce you to AstroHub, our groundbreaking global platform designed specifically for astrological events. Recognizing the challenges of connecting and sharing our passion for astrology across scattered social media groups and individual websites, we have created a unified space to bring our diverse community together.</p>\r\n      <p>This project is inspired and driven by professional astrologer <a href=\"https://morinus-astrology.com/alexei-borealis/\" rel=\"noopener noreferrer\" target=\"_blank\">Alexey Borealis</a>.\r\n      <h2>Why Join AstroHub?</h2>\r\n      <p><b>Amplify Your Reach:</b> Share event announcements, articles, and engaging content effortlessly. Our platform is a powerful, free marketing tool designed to amplify your reach.</p>\r\n      <p><b>Automatic Social Sharing:</b> Let our automated social media reposting feature spread your content across multiple channels, boosting your visibility with minimal effort.</p>\r\n      <p><b>Boost Your Visibility:</b> Our built-in SEO tools ensure your events and articles rank high in search results, making it easy for a global audience to find you.</p>\r\n      <p><b>Specialized Formatting Tools:</b> Enhance your posts with astrological fonts, support for mathematical formulas, and rapid content loading. Present your announcements professionally and appealingly.</p>\r\n      <p><b>Mobile-Optimized</b> Enjoy full mobile optimization, ensuring your content looks perfect and is accessible on any device, anytime, anywhere.</p>\r\n      <p><b>Global Engagement:</b> Connect with a wider, more engaged audience. Join AstroHub to be at the forefront of the astrological community, reaching enthusiasts and professionals worldwide.</p>\r\n      <p><b>Free Marketing:</b> Use AstroHub as a no-cost marketing tool. We actively promote your posts and articles, ensuring they get the attention they deserve.</p>\r\n      <p><a href=\"/registration/\">Join us</a> and be among the first to leverage this innovative platform. Together, we can build a thriving, interconnected astrological community.</p>\r\n    </div>\r\n  </div>\r\n</div>','2024-06-08 09:09:49.389387','2024-06-11 07:28:26.386179',0,0),(4,'Who Can Register?','Registration Steps - Astrological Events Worldwide','How to register on the astrological event aggregator and share news and events from your astrological community','static/img/page/registration.jpg','Registration Steps','registration','<div class=\"container py-5 my-5 post\">\r\n  <div class=\"row\">\r\n    <div class=\"col col-md-8 mx-auto\">\r\n      <h1 class=\"font-title\">Who Can Register</h1>\r\n      <p>Any representative of an astrological community—schools, publishers, lodges, associations or just an individual astrologer—can register on our site.</p>\r\n      <h2>Why Register?</h2>\r\n      <p><b>Maximize Your Reach:</b> Publish not only event announcements but also insightful articles and engaging content. Our platform isn\'t just a space for sharing; it\'s a powerful, free marketing tool that significantly amplifies your reach.</p>\r\n      <p><b>Automatic Social Media Reposting:</b> Save time and effort with our automated social media reposting feature. Once you publish on AstroHub, your content will be seamlessly shared across various social media channels, ensuring maximum visibility with minimal effort.</p>\r\n      <p><b>Enhanced SEO Optimization:</b> Gain greater online visibility with our built-in SEO optimization mechanisms. Your events and articles will be optimized for search engines, making it easier for a global audience to discover your content.</p>\r\n      <p><b>Connect Globally:</b> Engage with a wider, more engaged audience. By joining AstroHub, your organization will be at the forefront of the astrological community, reaching enthusiasts and professionals worldwide.</p>\r\n      <p><b>Free Marketing Tool:</b> Utilize AstroHub as a no-cost marketing instrument to promote your events and insights. We are committed to actively promoting your posts and articles, ensuring they receive the attention they deserve.</p>\r\n      <p><b>Advanced Formatting Tools:</b> Utilize specialized formatting tools designed for astrologers, including astrological fonts, support for mathematical formulas, and rapid content loading. Our platform ensures your announcements and posts are presented in the most professional and appealing manner possible.</p>\r\n      <p>We are inviting leading astrological organizations to be among the first to leverage this innovative platform. Together, we can build a thriving, interconnected astrological community.</p>\r\n      <h2>Registration Steps</h2>\r\n      <p>Getting started is simple.</p>\r\n      <h3>Step 1. Send Request</h3>\r\n      <p>Send a request email to <code>info@astrohub.events</code>, providing the following details:</p>\r\n      <ul>\r\n        <li>The name and your website or one of your astrological organization,</li>\r\n        <li>If you\'re using a public email service (e.g., Gmail, Yahoo), please provide a link to a page on your website where your email address is visible. This will help us verify your affiliation with the person/organization who is registering.</li>\r\n      </ul>\r\n      <h3>Receive Login Credentials</h3>\r\n      <p>Once your application is reviewed and approved, expect to receive your login credentials via email promptly.</p>\r\n      <h3>Step3. Publish Your Events and Articles</h3>\r\n      <p>After receiving your login credentials, you\'ll gain access to publish events on behalf of your organization. Additionally, you can showcase your astrological insights and style through engaging blog posts. What\'s more, your content will automatically be reposted across rapidly expanding social networks. We have modern and reach publishing tools for you. See <a href=\"/site-usage/\">more information here</a>.</p>\r\n      <p>Your articles will be automatically optimized for SEO. We believe that the power of social media and SEO boosts your publications to the peak of recognition.</p>\r\n    </div>\r\n  </div>\r\n</div>','2024-06-08 09:49:07.998591','2024-06-11 07:13:58.287941',0,0),(5,'How to Use the Site','Maximize Your Site\'s Potential: Tips for Effective Use','Unlock the full potential of this site. Learn to manage content, and embrace special features for optimal results','static/img/page/site-usage.jpg','How to Use the Site','site-usage','<div class=\"container py-5 my-5 post\">\r\n  <div class=\"row\">\r\n    <div class=\"col col-md-8 mx-auto\" id=\"content\">\r\n      <h1 class=\"font-title\">How to Use the Site</h1>\r\n      <p>Once registered, you\'ll have access to the admin panel, where you can:</p>\r\n      <ul>\r\n        <li>Update information about your astrological organization.</li>\r\n        <li>Add and edit your astrological events.</li>\r\n      </ul>\r\n      <div>\r\n      <img class=\"w-100 py-2\" src=\"/static/img/page/dashboard.webp\">\r\n      </div>\r\n      <p>The dashboard interface is intuitive.</p>\r\n      <h2>Blog Posting</h2>\r\n      <p>To showcase your astrological style, you can publish astrological articles. Here\'s how:</p>\r\n      <p><b>1. Create Authors</b></p>\r\n      <ul>\r\n        <li>Add astrologers from your community who will be credited as authors of the articles.</li>\r\n        <li>You can also add yourself as an author to publish articles under your name.</li>\r\n      </ul>\r\n      <p><b>2. Publish Articles:</b></p>\r\n      <ul>\r\n        <li>Publish articles authored by the created authors.</li>\r\n        <li>You can also publish articles under your name by adding yourself as the author of a particular article.</li>\r\n      </ul>\r\n      <h2>Recommendations for Publishing Articles and Events</h2>\r\n      <p><b>Markdown Support:</b></p> \r\n      <p>We support Markdown formatting. You can learn more about this formatting style <a href=\"https://support.typora.io/Markdown-Reference/\" rel=\"noreferrer noopener\" target=\"_blank\">here</a>.</p>\r\n      <p>To insert images that look good on both desktop and mobile screens, please use the following code:</p>\r\n      <div class=\"card mb-5\">\r\n        <div class=\"card-body\">\r\n          <code>\r\n            &lt;div class=\"col col-md-8 mx-auto\"&gt;<br>\r\n            &lt;img class=\"w-100\" src=\"your_image_url\" alt=\"your_image_description\"&gt;<br>\r\n            &lt;/div&gt;\r\n          </code>\r\n        </div>\r\n      </div>\r\n      <p><b>Table of Contents:</b></p>\r\n      <p>If your article is long, you can include a table of contents by adding the tag \"[toc]\" in a separate paragraph.</p>\r\n      <div class=\"card\">\r\n        <div class=\"card-body\">\r\n          <code>\r\n            ...<br>\r\n            [toc]<br>\r\n            ...\r\n          </code>\r\n        </div>\r\n      </div>\r\n      <p>It will be translated into:</p>\r\n      <p>[toc]</p>\r\n      <p><b>Mathematical Formulas:</b></p>\r\n      <p>If you use inline formulas, wrap them into \"$\" symbols, f.e. <code>$E=mc^2$</code> will be translated to $E=mc^2$.</p>\r\n      <p>If you use formulas as a separate block between paragraph, please wrap them with the following:</p>\r\n      <div class=\"card\">\r\n        <div class=\"card-body\">\r\n          <code>\r\n            &lt;div class=\"overflow-auto py-2\"&gt;<br>\r\n            $$<br>\r\n            E=mc^2\\tag{1}<br>\r\n            $$<br>\r\n            &lt;/div\"&gt;<br>\r\n          </code>\r\n        </div>\r\n      </div>\r\n      <p>It will be translated to:</p>\r\n      <div>\r\n        $$\r\n          E=mc^2\\tag{1}\r\n        $$\r\n      </div>\r\n      <p><b>Astrological Fonts:</b></p>\r\n      <p>We support astrological fonts. To use them, click the \"include astrofont\" checkbox when editing your article. Then, wrap the symbols into the</p> \r\n      <p><code>&lt;span class=\"text-astro\"&gt;Symbols&lt;/span&gt;</code></p>\r\n      <p>For instance <code>&lt;span class=\"text-astro\"&gt;eW&lt;/span&gt;</code> will be translated to <span class=\"text-astro\">eW</span>. For full reference of symbols, see <a href=\"https://www.fonts4free.net/hamburgsymbols-font.html\" rel=\"noreferrer noopener\" target=\"_blank\">astrological font character map</a>.</p>\r\n      <p><b>SEO Tips:</b></p>\r\n      <p>To ensure search engines quickly rank your articles or events high in search results, follow your dashboard\'s recommended lengths for SEO titles and descriptions.</p>\r\n      <p>Following these guidelines, you can effectively manage your organization\'s presence on our site and reach a global audience.</p>\r\n    </div>\r\n  </div>\r\n</div>','2024-06-08 10:17:19.610929','2024-06-08 23:44:17.117348',1,1),(6,'Terms of Use','erms of Use Agreement: Legal Responsibilities & Guidelines','Understand legal obligations on our platform. Learn responsibilities, content guidelines, and administrative actions.','static/img/page/terms-of-use.jpg','Terms of Use','terms-of-use','<div class=\"container py-5 my-5 post\">\r\n  <div class=\"row\">\r\n    <div class=\"col col-md-8 mx-auto\" id=\"content\">\r\n      <h1 class=\"font-title\">Terms of Use</h1>\r\n      <h2>For Visitors</h2>\r\n      <p><b>1. Content Responsibility</b></p>\r\n      <p>The site administration hereby disclaims all liability for the content and links posted by registered users. Visitors retain the right to report any content they believe violates applicable laws, incites hatred, or is offensive. In such instances, the administration reserves the right to take appropriate action, including removing said content.</p>\r\n      <p><b>2. User-Generated Links</b></p>\r\n      <p>Visitors acknowledge and agree to assume full responsibility for their actions when navigating external links posted by other users on the site. They do so at their own risk and discretion.</p>\r\n      <h2> For Registered Users</h2>\r\n      <p><b>1. Content Responsibility</b></p>\r\n      <p>By registering on this site, users agree to accept full responsibility for all content they contribute. They warrant that such content does not incite hatred, violate applicable laws, or offend the sensibilities of others. Users further agree to indemnify and hold harmless the site administration against any claims arising from their content.</p>\r\n      <p><b>2. Link Responsibility</b></p>\r\n      <p>Registered users are solely responsible for the operational integrity of any links they post on the site. They affirm that said links do not direct users to sites that contravene laws or regulations.</p>\r\n      <p><b>3. Administrative Actions</b></p>\r\n      <p>The site administration reserves the sole and absolute discretion to block or terminate any user\'s account in violation of these terms of use. Additionally, the administration may remove any content deemed to breach these terms without prior notice.</p>\r\n     <h2>Terms Updates</h2>\r\n     <p>We reserve the right to update these Terms without notification. Any changes will be \r\neffective immediately upon posting on the website.</p>\r\n      <p>By accessing or using this site, visitors and registered users acknowledge that they have read, understood, and agree to be bound by these terms of use. These terms constitute a legally binding user and site administration agreement.</p>\r\n    </div>\r\n  </div>\r\n</div>','2024-06-08 12:40:43.710025','2024-06-08 15:30:50.098539',0,0),(7,'Privacy Policy','Privacy Policy: User Data Collection & Protection Guidelines','Learn how we collect and protect user data. Understand our policies for data storage, deletion, and user consent.','static/img/page/privacy-policy.jpg','Privacy Policy','privacy-policy','<div class=\"container py-5 my-5 post\">\r\n  <div class=\"row\">\r\n    <div class=\"col col-md-8 mx-auto\" id=\"content\">\r\n      <h1 class=\"font-title\">Privacy Policy</h1>\r\n      <p>This Privacy Policy governs the collection, use, and disclosure of personal information provided by registered users of our website.</p>\r\n      <p><b>1. Information Collection</b></p>\r\n      <p>We collect limited personal information from registered users, specifically email addresses and names. This information is necessary for user authentication and communication purposes.</p>\r\n      <p><b>2. Information Usage</b></p>\r\n      <p>The personal information collected is strictly used for user login and communication within the platform. It is not visible to other users and is not shared with third parties.</p>\r\n      <p><b>3. Data Storage</b></p>\r\n      <p>All user data is securely stored on servers located at Hetzner in Germany. We maintain robust security measures to protect this data from unauthorized access or disclosure.</p>\r\n      <p><b>4. Data Deletion</b></p>\r\n      <p>Upon user request, we can [permanently delete your data from our servers. However, it\'s important to note that such action will result in the user losing access to their account and associated services.</p>\r\n      <p><b>5. Policy Updates</b></p>\r\n      <p>We reserve the right to update this Privacy Policy at any time. Any changes will be effective immediately upon posting on the website.</p>\r\n      <p>By using our website and providing personal information, registered users consent to collecting and using their information as outlined in this Privacy Policy.</p>\r\n    </div>\r\n  </div>\r\n</div>','2024-06-08 12:57:53.879484','2024-06-08 15:30:35.439167',0,0),(8,'Cookie Policy','Cookie Policy: Usage and GDPR Compliance Explained','Learn about our cookie usage for theme preference, user authentication, and traffic analysis. GDPR compliant.','static/img/page/cookie-policy.jpg','Cookie Policy','cookie-policy','<div class=\"container py-5 my-5 post\">\r\n  <div class=\"row\">\r\n    <div class=\"col col-md-8 mx-auto\" id=\"content\">\r\n      <h1 class=\"font-title\">Cookie Policy</h1>\r\n      <p>This Cookie Policy explains how our website uses cookies to enhance user experience. By using our website, you consent to using cookies by this policy.</p>\r\n      <p><b>1. What Are Cookies?</b></p>\r\n      <p>Cookies are small text files placed on your device by websites you visit. They are widely used to make websites work more efficiently and to provide information to the site owners.</p>\r\n      <p><b>2. Types of Cookies We Use:</b></p>\r\n      <p>a. Third-Party Cookies</p>\r\n      <ul>\r\n        <li>Google Analytics:  We use Google Analytics to analyze website traffic and user behavior. These cookies help us understand how visitors interact with our site, allowing us to improve user experience. The information collected is anonymous and used solely for analytical purposes.</li>\r\n      </ul>\r\n      <p>b. Internal Cookies</p>\r\n      <ul>\r\n        <li>Theme Preference: We use cookies to remember your theme preference (light or dark mode). This ensures a consistent and personalized user experience across sessions.</li>\r\n        <li>User Authentication: We use cookies to authenticate registered users. These cookies are essential for securely logging in and accessing user-specific features of the site.</li>\r\n      </ul>\r\n      <p><b>3. Managing Cookies</b></p>\r\n      <p>You can manage or delete cookies as you wish. Most web browsers allow you to control cookies through the browser settings. However, disabling cookies may affect our website\'s functionality and your experience.</p>\r\n      <p><b>4. Changes to This Policy</b></p>\r\n      <p>We may update this Cookie Policy from time to time to reflect changes in our practices or for other operational, legal, or regulatory reasons. Any changes will be posted on this page.</p>\r\n      <p>By continuing to use our website, you agree to the placement of cookies on your device as described in this Cookie Policy.</p>\r\n    </div>\r\n  </div>\r\n</div>','2024-06-08 15:38:16.214979','2024-06-08 15:38:16.215011',0,0);
/*!40000 ALTER TABLE `static_pages_page` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-28 11:03:22
