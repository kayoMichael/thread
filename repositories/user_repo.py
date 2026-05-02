from db.connection import get_cursor

def get_user(uid: int):
    """Fetch a single user row by id."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (uid, ))
        return cur.fetchone()

def create_user(username: str, password: str):
    """Insert a new user with the given username and password."""
    with get_cursor() as cur:
        cur.execute("""
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                    """, (username, password))

def delete_user(uid: int):
    """Hard-delete a user. Cascades to their posts, comments, and post_votes via FK."""
    with get_cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (uid,))
