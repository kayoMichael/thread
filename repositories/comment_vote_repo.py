from db.connection import get_cursor
from typing import Literal


def upsert_comment_vote(user_id: int, comment_id: int, vote_type: Literal[1, 0, -1]):
    """Set, change, or clear a user's vote on a comment.

    `vote_type` of 1 (upvote) or -1 (downvote) inserts a new vote row, or
    updates the existing one if the user has already voted on this comment.
    `vote_type` of 0 removes the user's vote entirely.
    """
    if vote_type == 0:
        with get_cursor() as cur:
            cur.execute("""
                        DELETE FROM comment_votes WHERE user_id = %s AND comment_id = %s
                        """, (user_id, comment_id))
    else:
        with get_cursor() as cur:
            cur.execute("""
                        INSERT INTO comment_votes (user_id, comment_id, vote_type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, comment_id) DO UPDATE SET vote_type = EXCLUDED.vote_type, updated_at = NOW()
                        WHERE comment_votes.vote_type IS DISTINCT FROM EXCLUDED.vote_type
                        """, (user_id, comment_id, vote_type))

def comment_vote_count(comment_id: int):
    """Return the total number of votes (up + down combined) on a comment."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT COUNT(*)
                    FROM comment_votes
                    WHERE comment_id = %s
                    """, (comment_id,))

        vote_count = cur.fetchone()[0]
        return vote_count
    

def comment_vote_score(comment_id: int):
    """Return the total vote score (up = 1, down = -1) on a comment."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT SUM(vote_type)
                    FROM comment_votes
                    WHERE comment_id = %s
                    """, (comment_id,))
        
        vote_score = cur.fetchone()
        return vote_score
