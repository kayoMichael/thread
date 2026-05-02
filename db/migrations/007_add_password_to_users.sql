--migrate:up
ALTER TABLE users ADD COLUMN password VARCHAR(255) NOT NULL

--migrate:down
ALTER TABLE users DROP COLUMN password