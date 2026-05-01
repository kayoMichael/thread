WITH RECURSIVE comment_replies AS (
    SELECT id, post_id, comment_id, comment_text
    FROM comments
    WHERE id = %s

    UNION ALL

    SELECT child.id, child.post_id, child.comment_id, child.comment_text
    FROM comments child
    JOIN comment_replies parent ON parent.id = child.comment_id
    WHERE child.deleted_at IS NOT NULL
)

CYCLE id SET is_cycle USING path
SELECT * FROM comment_replies
WHERE NOT is_cycle