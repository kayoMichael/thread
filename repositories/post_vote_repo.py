from typing import Literal
from db.connection import get_cursor

def upsert_post_vote(user_id: int, post_id: int, vote_type: Literal[-1, 0, 1]):
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
    

