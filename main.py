"""Demo entrypoint.

Walks the schema end-to-end: seeds a few users, a post, a small threaded
comment tree, and some votes, then prints the recursive views.

"""

from db.connection import get_cursor
from repositories import (
    user_repo,
    posts_repo,
    comment_repo,
    post_vote_repo,
    comment_vote_repo,
)

DEMO_USERS = ("alice", "bob", "carol")


def reset_demo_data() -> None:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM users WHERE username = ANY(%s)",
            (list(DEMO_USERS),),
        )


def get_user_id(username: str) -> int:
    with get_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        return cur.fetchone()[0]


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def main() -> None:
    reset_demo_data()

    section("seeding users")
    for name in DEMO_USERS:
        user_repo.create_user(name, "pw")
    alice, bob, carol = (get_user_id(n) for n in DEMO_USERS)
    print(f"alice={alice}  bob={bob}  carol={carol}")

    section("creating a post")
    post_id = posts_repo.create_post(
        "Hello world",
        "first post on the dev box",
        alice,
    )[0]
    print(f"post_id={post_id}")

    section("building a comment thread")
    c1 = comment_repo.create_comment(post_id, "great post", alice, None)
    c2 = comment_repo.create_comment(None, "thanks!", bob, c1)
    c3 = comment_repo.create_comment(None, "agreed", carol, c2)
    c4 = comment_repo.create_comment(post_id, "anything else?", bob, None)
    print(f"c1={c1}  c2={c2}  c3={c3}  c4={c4}")

    section("casting votes")
    post_vote_repo.upsert_post_vote(bob, post_id, 1)
    post_vote_repo.upsert_post_vote(carol, post_id, 1)
    comment_vote_repo.upsert_comment_vote(alice, c2, 1)
    comment_vote_repo.upsert_comment_vote(carol, c2, 1)
    comment_vote_repo.upsert_comment_vote(bob, c3, -1)
    print(f"post score:  {post_vote_repo.post_vote_score(post_id)}")
    print(f"c2 score:    {comment_vote_repo.comment_vote_score(c2)}")
    print(f"c2 replies:  {comment_repo.comment_replies_count(c2)}")

    section("post_thread (recursive — every live comment under the post)")
    for row in comment_repo.get_post_thread(post_id):
        print(row)

    section("comment_ancestors (walk c3 up to its post root)")
    for row in comment_repo.get_comment_ancestors(c3):
        print(row)

    section("comment_replies (descendants of c1, with vote scores)")
    for row in comment_repo.get_comment_replies(c1):
        print(row)

    section("soft-deleting c2 subtree")
    comment_repo.soft_delete_comment(c2)
    print("post_thread after delete:")
    for row in comment_repo.get_post_thread(post_id):
        print(row)


if __name__ == "__main__":
    main()
