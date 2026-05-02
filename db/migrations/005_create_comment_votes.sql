--migrate:up
CREATE TABLE comment_votes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    comment_id BIGINT REFERENCES comments(id),
    vote_type SMALLINT NOT NULL CHECK (vote_type IN (-1, 1)),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_comment_vote UNIQUE(user_id, comment_id)
)

--migrate:down
DROP TABLE comment_votes;