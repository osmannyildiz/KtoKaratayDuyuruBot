SET autocommit = 0;
START TRANSACTION;

USE kkdb;

ALTER TABLE website_faculty_channels ADD disable_website_check BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE website_department_channels ADD disable_website_check BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE website_misc_channels ADD disable_website_check BOOLEAN NOT NULL DEFAULT false;

COMMIT;
