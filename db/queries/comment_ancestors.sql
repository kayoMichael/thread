WITH RECURSIVE 
    comment_ancestors AS (
        SELECT c.id, c.comment_id, c.post_id, c.comment_text, p.title, p.body
        FROM comments c
        LEFT JOIN posts p ON p.id = c.post_id
        WHERE c.id = %s

        UNION ALL

        SELECT parent.id, parent.comment_id, parent.post_id, parent.comment_text, p.title, p.body
        FROM comments parent
        JOIN comment_ancestors child ON child.comment_id = parent.id
        LEFT JOIN posts p ON p.id = parent.post_id
    ) CYCLE id SET is_cycle USING PATH,
    score_by_comment AS (
        SELECT comment_id, SUM(vote_type) AS comment_score
        FROM comment_votes
        GROUP BY comment_id
    ),
    score_by_post AS (
        SELECT post_id, SUM(vote_type) AS post_score
        FROM post_votes
        GROUP BY post_id
    )

SELECT ca.*, sc.comment_score, sp.post_score
FROM comment_ancestors ca
LEFT JOIN score_by_comment sc ON sc.comment_id = ca.id
LEFT JOIN score_by_post sp ON sp.post_id = ca.post_id
WHERE NOT ca.is_cycle