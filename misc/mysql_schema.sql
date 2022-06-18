DROP DATABASE IF EXISTS kkdb;
CREATE DATABASE kkdb;
USE kkdb;

CREATE TABLE faculties (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	code					VARCHAR(255)	NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE departments (
	id						INT				NOT NULL AUTO_INCREMENT,
	faculty_id				INT				NOT NULL,
	name					VARCHAR(255)	NOT NULL,
	code					VARCHAR(255)	DEFAULT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (faculty_id) REFERENCES faculties(id)
);

CREATE TABLE users (
	id						INT				NOT NULL AUTO_INCREMENT,
	chat_id					VARCHAR(255)	NOT NULL UNIQUE,
	state					VARCHAR(255)	NOT NULL,
	faculty_id				INT				DEFAULT NULL,
	department_id			INT				DEFAULT NULL,
	bot_last_msg_id			INT				DEFAULT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (faculty_id) REFERENCES faculties(id),
	FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE kkdb_special_channels (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	subscribe_by_default	BOOLEAN			NOT NULL DEFAULT false,
	PRIMARY KEY (id)
);

CREATE TABLE website_faculty_channels (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	faculty_id				INT				NOT NULL,
	last_announcement_id	INT				DEFAULT NULL,
	disable_website_check	BOOLEAN			NOT NULL DEFAULT false,
	PRIMARY KEY (id),
	FOREIGN KEY (faculty_id) REFERENCES faculties(id)
);

CREATE TABLE website_department_channels (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	department_id			INT				NOT NULL,
	last_announcement_id	INT				DEFAULT NULL,
	disable_website_check	BOOLEAN			NOT NULL DEFAULT false,
	PRIMARY KEY (id),
	FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE website_misc_channels (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	url						VARCHAR(255)	NOT NULL,
	last_announcement_id	INT				DEFAULT NULL,
	subscribe_by_default	BOOLEAN			NOT NULL DEFAULT false,
	disable_website_check	BOOLEAN			NOT NULL DEFAULT false,
	PRIMARY KEY (id)
);

CREATE TABLE kkdb_special_channels_subscriptions (
	id						INT				NOT NULL AUTO_INCREMENT,
	user_id					INT				NOT NULL,
	channel_id				INT				NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (channel_id) REFERENCES kkdb_special_channels(id)
);

CREATE TABLE website_faculty_channels_subscriptions (
	id						INT				NOT NULL AUTO_INCREMENT,
	user_id					INT				NOT NULL,
	channel_id				INT				NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (channel_id) REFERENCES website_faculty_channels(id)
);

CREATE TABLE website_department_channels_subscriptions (
	id						INT				NOT NULL AUTO_INCREMENT,
	user_id					INT				NOT NULL,
	channel_id				INT				NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (channel_id) REFERENCES website_department_channels(id)
);

CREATE TABLE website_misc_channels_subscriptions (
	id						INT				NOT NULL AUTO_INCREMENT,
	user_id					INT				NOT NULL,
	channel_id				INT				NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (channel_id) REFERENCES website_misc_channels(id)
);

CREATE TABLE stats (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	item_id					INT				DEFAULT NULL,
	value					INT				NOT NULL,
	PRIMARY KEY (id)
);

