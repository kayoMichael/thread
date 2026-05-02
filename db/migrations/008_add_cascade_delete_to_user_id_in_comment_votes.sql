--migrate:up
ALTER TABLE comment_votes ADD CONSTRAINT fk_comment_votes_user_id
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

--migrate:down
ALTER TABLE comment_votes DROP CONSTRAINT fk_comment_votes_user_id;