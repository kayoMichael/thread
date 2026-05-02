WITH RECURSIVE delete_comment AS (
    SELECT id FROM comments WHERE id = %s

    UNION ALL

    SELECT c.id
    FROM comments c
    JOIN delete_comment d ON c.comment_id = d.id
)

UPDATE comments SET deleted_at = NOW()
WHERE id IN (SELECT id FROM delete_comment) AND deleted_at IS NULL
