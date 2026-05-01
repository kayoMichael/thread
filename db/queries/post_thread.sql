WITH RECURSIVE post_comment_thread AS (
    SELECT c.*
    FROM comments c WHERE c.post_id = %s AND c.deleted_at IS NOT NULL

    UNION ALL

    SELECT c.*
    FROM comments c
    JOIN post_comment_thread parent ON parent.id = c.comment_id 
    WHERE c.deleted_at IS NOT NULL
)

CYCLE id SET is_cycle USING PATH
SELECT * FROM post_comment_thread
WHERE NOT is_cycle