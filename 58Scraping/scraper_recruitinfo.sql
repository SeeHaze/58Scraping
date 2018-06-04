/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 50717
Source Host           : localhost:3306
Source Database       : scraper_58

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2018-06-02 15:14:48
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for scraper_recruitinfo
-- ----------------------------
DROP TABLE IF EXISTS `scraper_recruitinfo`;
CREATE TABLE `scraper_recruitinfo` (
  `fid` int(11) NOT NULL AUTO_INCREMENT COMMENT '标识符',
  `fjobtitle` varchar(100) DEFAULT NULL COMMENT '职位标题',
  `fjobname` varchar(100) DEFAULT NULL COMMENT '职位名称',
  `fjobdescription` varchar(255) DEFAULT NULL COMMENT '职位描述',
  `fwages` varchar(50) DEFAULT NULL COMMENT '工资',
  `fcompanyname` varchar(50) DEFAULT NULL COMMENT '公司名称',
  `fcompanyinfo` varchar(255) DEFAULT NULL COMMENT '公司信息',
  `feducation` varchar(20) DEFAULT NULL COMMENT '学历',
  `feducationremark` varchar(50) DEFAULT NULL COMMENT '学历备注',
  `fNumberofpeople` varchar(10) DEFAULT NULL COMMENT '人数',
  `faddress` varchar(100) DEFAULT NULL COMMENT '地址',
  PRIMARY KEY (`fid`)
) ENGINE=InnoDB AUTO_INCREMENT=5865816 DEFAULT CHARSET=utf8;
