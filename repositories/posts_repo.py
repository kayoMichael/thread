from db.connection import get_cursor
from typing import Optional

def create_post(title: str, body: str, author_id: int) -> int:
    """Insert a new post authored by `author_id` and returns the post id."""
    with get_cursor() as cur:
        cur.execute("""
                    INSERT INTO posts (title, body, author_id)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """, (title, body, author_id))
        
        return cur.fetchone()


def update_post(post_id: int, title: Optional[str], body: Optional[str]):
    """Patch a post's title and/or body. Pass `None` for a field to leave it unchanged.
    """
    with get_cursor() as cur:
        cur.execute("""
                    UPDATE posts SET title = COALESCE(%s, title), body = COALESCE(%s, body), updated_at = NOW() WHERE id = %s
                    RETURNING updated_at
                    """, (title, body, post_id))

def delete_post(post_id: int):
    """Hard-delete a post. Cascades to its comments and post_votes via FK."""
    with get_cursor() as cur:
        cur.execute("""
                    DELETE FROM posts WHERE id = %s
                    """, (post_id, ))

def read_post(post_id: int):
    """Fetch a single post by id."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT * FROM posts WHERE id = %s
                    """, (post_id,))
        
        return cur.fetchall()

def get_all_user_posts(user_id: int):
    """Return every post authored by the given user."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT p.id, p.author_id, p.title, p.body, p.created_at, p.updated_at
                    FROM users u
                    JOIN posts p ON p.author_id = u.id
                    WHERE u.id = %s
                    """, (user_id,))
        
        return cur.fetchall()

def get_posts_user_commented_on(user_id: int):
    """Return every posts the given user has voted on, with their vote type.
    (Replies don't count)
    """
    with get_cursor() as cur:
        cur.execute("""
                    SELECT p.*, v.vote_type
                    FROM posts p
                    JOIN post_votes v ON p.id = v.comment_id
                    """, (user_id,))

        return cur.fetchall()