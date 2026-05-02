# Entity Relationship Schema

Reference for the current PostgreSQL schema. Reflects [db/schema.sql](schema.sql)

## Diagram

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│    users    │1───────*│    posts    │1───────*│   comments   │
│             │         │             │         │              │
│ id (PK)     │         │ id (PK)     │         │ id (PK)      │
│ username    │         │ author_id   │─┐       │ author_id    │─┐
│ password    │         │ title       │ │       │ post_id      │ │
│ created_at  │         │ body        │ │       │ comment_id   │─┼─┐  (self-ref)
│ updated_at  │         │ created_at  │ │       │ comment_text │ │ │
└──────┬──────┘         │ updated_at  │ │       │ created_at   │ │ │
       │                └──────┬──────┘ │       │ updated_at   │ │ │
       │                       │        │       │ deleted_at   │ │ │
       │                       │        │       └──────┬───────┘ │ │
       │                       │        │              │         │ │
       │                       │        └──────────────┼─────────┘ │
       │                       │                       │           │
       │                       │                       └───────────┘
       │                       │
       │                       │
       │  ┌──────────────┐     │       ┌──────────────────┐
       └─*│  post_votes  │*────┘   ┌──*│  comment_votes   │*─┐
          │              │         │   │                  │  │
          │ id (PK)      │         │   │ id (PK)          │  │
          │ user_id (FK) │         │   │ user_id (FK)     │  │
          │ post_id (FK) │         │   │ comment_id (FK)  │  │
          │ vote_type    │         │   │ vote_type        │  │
          │ created_at   │         │   │ created_at       │  │
          │ updated_at   │         │   │ updated_at       │  │
          └──────────────┘         │   └──────────────────┘  │
                 ▲                 │            ▲            │
                 │                 │            │            │
                 └─────────────────┘            └────────────┘
                  user_id → users         (user_id → users,
                                           comment_id → comments)
```

## Tables

### `users`
Application accounts.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `username` | `varchar(50)` | NOT NULL, UNIQUE |
| `password` | `varchar(255)` | NOT NULL (added in migration 007) |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

### `posts`
Top-level posts authored by a user.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `author_id` | `bigint` | FK → `users.id`, ON DELETE CASCADE |
| `title` | `varchar(100)` | NOT NULL |
| `body` | `text` | nullable |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

### `comments`
Comments on posts. Self-referential `comment_id` enables threaded replies.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `author_id` | `bigint` | FK → `users.id`, ON DELETE CASCADE |
| `post_id` | `bigint` | FK → `posts.id`, ON DELETE CASCADE |
| `comment_id` | `bigint` | FK → `comments.id` (parent comment, nullable for top-level) |
| `comment_text` | `text` | NOT NULL |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |
| `deleted_at` | `timestamptz` | nullable; soft delete |

### `post_votes`
Upvote / downvote of a post by a user. One vote per (user, post).

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `user_id` | `bigint` | FK → `users.id`, ON DELETE CASCADE |
| `post_id` | `bigint` | FK → `posts.id`, ON DELETE CASCADE |
| `vote_type` | `smallint` | NOT NULL, CHECK IN (-1, 1) |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

UNIQUE (`user_id`, `post_id`).

### `comment_votes`
Upvote / downvote of a comment by a user. One vote per (user, comment).

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `user_id` | `bigint` | FK → `users.id` (no cascade) |
| `comment_id` | `bigint` | FK → `comments.id` (no cascade) |
| `vote_type` | `smallint` | NOT NULL, CHECK IN (-1, 1) |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

UNIQUE (`user_id`, `comment_id`).

### `schema_migrations`
Managed by dbmate; tracks applied migration versions.

| Column | Type | Notes |
| --- | --- | --- |
| `version` | `varchar` | PK |

## Relationships

| From | To | Cardinality | On Delete |
| --- | --- | --- | --- |
| `posts.author_id` | `users.id` | many-to-one | CASCADE |
| `comments.author_id` | `users.id` | many-to-one | CASCADE |
| `comments.post_id` | `posts.id` | many-to-one | CASCADE |
| `comments.comment_id` | `comments.id` | many-to-one (self) | (none) |
| `post_votes.user_id` | `users.id` | many-to-one | CASCADE |
| `post_votes.post_id` | `posts.id` | many-to-one | CASCADE |
| `comment_votes.user_id` | `users.id` | many-to-one | (none) |
| `comment_votes.comment_id` | `comments.id` | many-to-one | (none) |

## Notes

- All primary keys are `bigint` identity columns (`GENERATED ALWAYS AS IDENTITY`).
- `vote_type` is constrained to `-1` (downvote) or `1` (upvote).
- `comments` uses soft delete via `deleted_at`; all other tables hard-delete.
- `comment_votes` FKs do not cascade on delete, unlike `post_votes` — deleting a user or comment will fail if related `comment_votes` rows exist.
