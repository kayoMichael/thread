from db.connection import get_cursor
from typing import Optional

def create_post(title: str, body: str, author_id: int):
    with get_cursor() as cur:
        cur.execute("""
                    INSERT INTO posts (title, body, author_id)
                    VALUES (%s, %s, %s)
                    """, (title, body, author_id))
        

def update_post(post_id: int, title: Optional[str], body: Optional[str]) -> int:
    with get_cursor() as cur:
        cur.execute("""
                    UPDATE posts SET title = COALESCE(%s, title), body = COALESCE(%s, body), updated_at = NOW() WHERE id = %s
                    """, (title, body, post_id))
        
        post_id = cur.fetchone()[0]

        return post_id

def delete_post(post_id: int):
    with get_cursor() as cur:
        cur.execute("""
                    DELETE FROM posts WHERE id = %s
                    """, (post_id, ))
