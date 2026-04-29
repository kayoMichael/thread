from db.connection import get_cursor

def get_user(uid):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM USER WHERE id = %s", (uid, ))
        return cur.fetchone()
