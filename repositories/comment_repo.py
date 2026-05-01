from db.connection import get_cursor, run_query
from typing import Optional

def create_comment(post_id: Optional[int], comment_text: str, author_id: int, comment_id: Optional[int]):
    """Insert a new comment.

    Exactly one of `post_id` or `comment_id` should be non-null:
    `post_id` is set when the immediate parent is a post; `comment_id` is set
    when the immediate parent is another comment.
    """
    with get_cursor() as cur:
        cur.execute("""
                    INSERT INTO comments (post_id, comment_text, author_id, comment_id)
                    VALUES (%s, %s, %s, %s)
                    """, (post_id, comment_text, author_id, comment_id))


def update_comment(comment_id: int, comment_text: str):
    """Edit the text of an existing comment, identified by id."""
    with get_cursor() as cur:
        cur.execute("""
                    UPDATE comments SET comment_text = %s WHERE id = %s
                    """, (comment_text, comment_id))


def fetch_top_level_comment(post_id: int, author_id: int):
    """Return one of the given author's top-level comments on a post (text only)."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT comment_text
                    FROM comments
                    WHERE post_id = %s AND author_id = %s AND comment_id IS NULL
                    """, (post_id, author_id))


        comment = cur.fetchone()
        return comment


def select_single_comment_by_id(comment_id: int):
    """Return a single comment row (text, author, parent comment) by id."""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT comment_text, author_id, comment_id
                    FROM comments
                    WHERE id = %s
                    """, (comment_id, ))

        comment = cur.fetchone()
        return comment


def get_comment_ancestors(comment_id: int):
    """Return the chain of ancestor comments from this comment up to the post root."""
    return run_query("comment_ancestors", (comment_id,))


def get_comment_replies(comment_id: int):
    """Return every descendant comment under the given comment, at any depth."""
    return run_query("comment_replies", (comment_id,))


def soft_delete_comment(comment_id: int):
    """Soft-delete a comment and all of its descendants by setting `deleted_at`."""
    return run_query("delete_comments", (comment_id,))

def get_all_comments_voted_by_user(user_id: int):
    """Return every comment the given user has voted on, with their vote type.

    """
    with get_cursor() as cur:
        cur.execute("""
                    SELECT c.id, c.author_id, c.post_id, c.comment_id, c.comment_text, cv.vote_type
                    FROM comment_votes cv
                    JOIN comments c ON c.id = cv.comment_id
                    WHERE cv.user_id = %s
                    """, (user_id,))

        return cur.fetchall()
    
def comment_replies_count(comment_id: int):
    """Reply count for a comment"""
    with get_cursor() as cur:
        cur.execute("""
                    SELECT COUNT(*)
                    FROM comments
                    WHERE comments.comment_id = %s
                    """, (comment_id,))
        
        return cur.fetchall()
