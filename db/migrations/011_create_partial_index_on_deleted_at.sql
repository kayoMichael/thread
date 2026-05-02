--migrate:up
CREATE INDEX idx_comments_deleted_at ON comments (deleted_at) WHERE deleted_at IS NULL

--migrate:down
DROP INDEX IF EXISTS idx_comments_deleted_at