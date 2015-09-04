-- Create main table here
-- We need db to automate recognition analysis
BEGIN TRANSACTION;
CREATE TABLE `plates` (
	`id`	INTEGER NOT NULL,
	`filename`	TEXT NOT NULL,
	`value`	TEXT NOT NULL,
	PRIMARY KEY(id)
);
COMMIT;
