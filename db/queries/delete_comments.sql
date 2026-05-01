WITH RECURSIVE delete_comment AS (
    SELECT * FROM comments WHERE id = %s

    UNION ALL

    SELECT * FROM comments
    WHERE comment_id IN (SELECT id FROM delete_comment)
)

UPDATE comments SET deleted_at = NOW() WHERE id IN (SELECT ID FROM delete_comment) AND deleted_at IS NOT NULL