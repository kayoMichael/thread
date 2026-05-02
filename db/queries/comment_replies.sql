WITH RECURSIVE 
    score_by_comment AS (
    SELECT comment_id, SUM(vote_type) AS score
    FROM comment_votes
    GROUP BY comment_id
) CYCLE id SET is_cycle USING PATH, 
    comment_replies AS (
    SELECT c.id, c.post_id, c.comment_id, c.comment_text
    FROM comments c
    WHERE c.id = %s AND c.deleted_at IS NULL

    UNION ALL

    SELECT child.id, child.post_id, child.comment_id, child.comment_text, COALESCE(scores.score, 0) AS score
    FROM comments child
    JOIN comment_replies parent ON parent.id = child.comment_id
    WHERE child.deleted_at IS NULL
)

CYCLE id SET is_cycle USING path
SELECT cr.*m COALESCE(s.score, 0) AS score 
FROM comment_replies cr
LEFT JOIN score_by_comment s on s.comment_id = cr.id
WHERE NOT cr.is_cycle