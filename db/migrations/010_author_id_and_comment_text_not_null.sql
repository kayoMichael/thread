--migrate:up
ALTER TABLE comments ALTER COLUMN author_id SET NOT NULL;
ALTER TABLE comments ALTER COLUMN comment_text SET NOT NULL;

--migrate:down
ALTER TABLE comments ALTER COLUMN author_id DROP NOT NULL;
ALTER TABLE comments ALTER COLUMN comment_text DROP NOT NULL;