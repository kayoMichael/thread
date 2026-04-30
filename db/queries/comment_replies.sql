WITH RECURSIVE comment_replies AS (
    SELECT id, post_id, comment_id, comment_text
    FROM comments
    WHERE id = %s

    UNION ALL

    SELECT id, post_id, comment_id, comment_text
    FROM comments child
    JOIN comment_replies parent ON parent.id = child.comment_id
)

CYCLE id SET is_cycle USING path
SELECT * FROM comment_replies
WHERE NOT is_cycle