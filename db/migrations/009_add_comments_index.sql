--migrate:up
CREATE INDEX idx_comments_comment_id ON comments (comment_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);

--migrate:down
DROP INDEX idx_comments_comment_id;
DROP INDEX idx_comments_post_id;