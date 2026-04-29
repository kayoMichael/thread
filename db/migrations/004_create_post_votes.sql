--migrate:up
CREATE TABLE post_votes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    post_id BIGINT REFERENCES posts(id) ON DELETE CASCADE,
    vote SMALLINT NOT NULL CHECK (vote IN (-1, 0, 1)),
    created_at TIMESTAMPTZ DEFAULT NOW()
)

--migrate:down
DROP TABLE post_votes;
