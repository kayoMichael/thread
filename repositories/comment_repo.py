from db.connection import get_cursor
from typing import Optional

def create_comment(post_id: Optional[str], comment_text: str, author_id: int, comment_id: Optional[int]):
    with get_cursor() as cur:
        cur.execute("""
                    INSERT INTO comments (post_id, comment_text, author_id, comment_id)
                    VALUES (%s, %s, %s, %s)
                    """, (post_id, comment_text, author_id, comment_id))
        

def update_comment(comment_id: int, comment_text: str):
    with get_cursor() as cur:
        cur.execute("""
                    UPDATE posts SET comment_text = %s WHERE id = %s
                    """, (comment_text, comment_id))
        

def delete_comment(comment_id: int):
    with get_cursor() as cur:
        cur.execute("""
                    DELETE FROM posts WHERE id = %s
                    """, (comment_id, ))