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
	code					VARCHAR(255)	NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (faculty_id) REFERENCES faculties(id)
);

CREATE TABLE channels (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	item_type				INT				NOT NULL,
	item_id					INT				DEFAULT NULL,
	last_announcement_id	INT				DEFAULT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id						INT				NOT NULL AUTO_INCREMENT,
	chat_id					VARCHAR(255)	NOT NULL UNIQUE,
	faculty_id				INT				DEFAULT NULL,
	department_id			INT				DEFAULT NULL,
	state					INT				NOT NULL DEFAULT 0,
	bot_last_msg_id			INT				DEFAULT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (faculty_id) REFERENCES faculties(id),
	FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE subscriptions (
	id						INT				NOT NULL AUTO_INCREMENT,
	user_id					INT				NOT NULL,
	channel_id				INT				NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE TABLE stats (
	id						INT				NOT NULL AUTO_INCREMENT,
	name					VARCHAR(255)	NOT NULL,
	item_id					INT				DEFAULT NULL,
	value					INT				NOT NULL,
	PRIMARY KEY (id)
);

