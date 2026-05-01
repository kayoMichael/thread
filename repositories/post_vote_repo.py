from typing import Literal
from db.connection import get_cursor

def upsert_post_vote(user_id: int, post_id: int, vote_type: Literal[-1, 0, 1]):
    """Set, change, or clear a user's vote on a post.

    `vote_type` of 1 (upvote) or -1 (downvote) inserts a new vote row, or
    updates the existing one if the user has already voted on this post.
    `vote_type` of 0 removes the user's vote entirely.
    """
    if vote_type == 0:
        with get_cursor() as cur:
            cur.execute("""
                        DELETE FROM post_votes
                        WHERE post_id = %s AND user_id = %s
                        """, (post_id, user_id))
    else:
        with get_cursor() as cur:
            cur.execute("""
                        INSERT INTO post_votes (user_id, post_id, vote_type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, post_id)
                        DO UPDATE SET vote_type = EXCLUDED.vote_type, updated_at = NOW()
                        WHERE post_votes.vote_type IS DISTINCT FROM EXCLUDED.vote_type;
                        """, (user_id, post_id, vote_type))
            
def post_vote_count(post_id):
    """Return the total number of votes (up + down combined) on a post."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT COUNT(*) FROM post_votes WHERE post_id = %s
                    """, (post_id, ))
        
        count = cur.fetchone()
        return count
    
def post_vote_score(post_id):
    """Return the total vote score (+1 up, -1 down) on a post."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT SUM(vote_type)
                    FROM post_votes
                    WHERE post_id = %s
                    """, (post_id, ))
        
        score = cur.fetchone()
        return score