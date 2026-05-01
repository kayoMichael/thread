--migrate:up
ALTER TABLE comment_votes ADD COLUMN updated_at TIMESTAMPTZ;

--migrate:down
ALTER TABLE comment_votes DROP COLUMN updated_at;