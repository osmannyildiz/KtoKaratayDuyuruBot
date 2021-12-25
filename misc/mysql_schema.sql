DROP DATABASE IF EXISTS kkdb;
CREATE DATABASE kkdb;
USE kkdb;

CREATE TABLE `users` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `faculty_id` int,
  `department_id` int,
  `state` int DEFAULT 0,
  `bot_last_msg_id` int
);

CREATE TABLE `faculties` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `code` varchar(255)
);

CREATE TABLE `departments` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `faculty_id` int,
  `name` varchar(255),
  `code` varchar(255)
);

CREATE TABLE `channels` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `item_type` int,
  `item_id` int,
  `last_announcement_id` int
);

CREATE TABLE `subscriptions` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int,
  `channel_id` int
);

CREATE TABLE `stats` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `item_id` int,
  `value` int
);

ALTER TABLE `users` ADD FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`);
ALTER TABLE `users` ADD FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`);
ALTER TABLE `departments` ADD FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`);
ALTER TABLE `subscriptions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `subscriptions` ADD FOREIGN KEY (`channel_id`) REFERENCES `channels` (`id`);
