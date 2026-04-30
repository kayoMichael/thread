WITH RECURSIVE comment_ancestors AS (
    SELECT c.id, c.comment_id, c.post_id, c.comment_text, p.title, p.body
    FROM comments c
    JOIN posts p ON p.id = c.post_id
    WHERE id = %s

    UNION ALL

    SELECT c.id, c.comment_id, c.post_id, c.comment_text, p.title, p.body
    FROM comments parent
    JOIN comment_ancestors child ON child.comment_id = parent.id
    JOIN posts p ON p.id = parent.post_id
)

SELECT * FROM comment_ancestors