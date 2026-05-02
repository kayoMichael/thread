# Threads

A small Reddit/HackerNews-style PostgreSQL backend exploring threaded comments, voting, and recursive SQL. The data layer is hand-written `psycopg` against a dbmate-managed schema, no ORM.

## Stack

- **Python 3.12** with [uv](https://docs.astral.sh/uv/) for env + dependency management
- **PostgreSQL 17** (via Docker Compose)
- **[dbmate](https://github.com/amacneil/dbmate)** for SQL migrations
- **[psycopg 3](https://www.psycopg.org/psycopg3/)** with `psycopg_pool` for connections
- **python-dotenv** for loading `DATABASE_URL`

## Project layout

```
.
├── db/
│   ├── connection.py        # pool, get_cursor(), run_query() loader
│   ├── migrations/          # dbmate migrations (001..011)
│   ├── queries/             # standalone .sql files loaded by run_query()
│   └── schema.sql           # dump produced by `dbmate dump`
├── repositories/            # one module per table — thin SQL wrappers
│   ├── user_repo.py
│   ├── posts_repo.py
│   ├── comment_repo.py
│   ├── post_vote_repo.py
│   └── comment_vote_repo.py
├── docker-compose.yml       # local Postgres 17
├── pyproject.toml
└── main.py
```

## Setup

### Prerequisites

Install the toolchain:

```sh
# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# dbmate (migration runner)
brew install dbmate
```

### Environment

Create `.env` in the project root:

```sh
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mydb?sslmode=disable"
```

`dbmate` and `db/connection.py` both read `DATABASE_URL` from this file.

### Start Postgres

```sh
docker compose up -d
```

### Install Python dependencies

```sh
uv sync
```

### Run migrations

```sh
dbmate up
```

### Run code

```sh
docker compose up
uv python main.py
```

## Schema

### ER diagram

```mermaid
erDiagram
    users {
        bigint id PK
        varchar(50) username UK
        varchar(255) password
        timestamptz created_at
        timestamptz updated_at
    }

    posts {
        bigint id PK
        bigint author_id FK
        varchar(100) title
        text body
        timestamptz created_at
        timestamptz updated_at
    }

    comments {
        bigint id PK
        bigint author_id FK
        bigint post_id FK
        bigint comment_id FK "self-ref, nullable"
        text comment_text
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at "soft delete"
    }

    post_votes {
        bigint id PK
        bigint user_id FK
        bigint post_id FK
        smallint vote_type "-1 or 1"
        timestamptz created_at
        timestamptz updated_at
    }

    comment_votes {
        bigint id PK
        bigint user_id FK
        bigint comment_id FK
        smallint vote_type "-1 or 1"
        timestamptz created_at
        timestamptz updated_at
    }

    users        ||--o{ posts         : authors
    users        ||--o{ comments      : authors
    users        ||--o{ post_votes    : casts
    users        ||--o{ comment_votes : casts
    posts        ||--o{ comments      : has
    posts        ||--o{ post_votes    : receives
    comments     ||--o{ comments      : replies_to
    comments     ||--o{ comment_votes : receives
```

### Tables

#### `users`
Application accounts.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `username` | `varchar(50)` | NOT NULL, UNIQUE |
| `password` | `varchar(255)` | NOT NULL |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

#### `posts`
Top-level posts authored by a user.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `author_id` | `bigint` | FK → `users.id`, ON DELETE CASCADE |
| `title` | `varchar(100)` | NOT NULL |
| `body` | `text` | nullable |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

#### `comments`
Comments on posts. Self-referential `comment_id` enables threaded replies.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `author_id` | `bigint` | NOT NULL, FK → `users.id`, ON DELETE CASCADE |
| `post_id` | `bigint` | FK → `posts.id`, ON DELETE CASCADE |
| `comment_id` | `bigint` | FK → `comments.id` (parent comment, nullable for top-level) |
| `comment_text` | `text` | NOT NULL |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |
| `deleted_at` | `timestamptz` | nullable; soft delete |

Indexes:
- `idx_comments_post_id` — btree on `post_id`
- `idx_comments_comment_id` — btree on `comment_id`
- `idx_comments_deleted_at` — partial btree on `deleted_at WHERE deleted_at IS NULL` (keeps live-comment lookups cheap)

#### `post_votes`
Upvote / downvote of a post by a user. One vote per `(user, post)`.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `user_id` | `bigint` | FK → `users.id`, ON DELETE CASCADE |
| `post_id` | `bigint` | FK → `posts.id`, ON DELETE CASCADE |
| `vote_type` | `smallint` | NOT NULL, CHECK IN (-1, 1) |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

UNIQUE (`user_id`, `post_id`).

#### `comment_votes`
Upvote / downvote of a comment by a user. One vote per `(user, comment)`.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK, identity |
| `user_id` | `bigint` | FK → `users.id`, ON DELETE CASCADE |
| `comment_id` | `bigint` | FK → `comments.id` (no cascade) |
| `vote_type` | `smallint` | NOT NULL, CHECK IN (-1, 1) |
| `created_at` | `timestamptz` | default `now()` |
| `updated_at` | `timestamptz` | nullable |

UNIQUE (`user_id`, `comment_id`).

#### `schema_migrations`
Managed by dbmate; tracks applied migration versions.

### Relationships

| From | To | Cardinality | On Delete |
| --- | --- | --- | --- |
| `posts.author_id` | `users.id` | many-to-one | CASCADE |
| `comments.author_id` | `users.id` | many-to-one | CASCADE |
| `comments.post_id` | `posts.id` | many-to-one | CASCADE |
| `comments.comment_id` | `comments.id` | many-to-one (self) | (none) |
| `post_votes.user_id` | `users.id` | many-to-one | CASCADE |
| `post_votes.post_id` | `posts.id` | many-to-one | CASCADE |
| `comment_votes.user_id` | `users.id` | many-to-one | CASCADE |
| `comment_votes.comment_id` | `comments.id` | many-to-one | (none) |


## Recursive queries

Threaded reads live as standalone SQL files in [db/queries/](db/queries/), loaded by `db.connection.run_query`:

| Query | Purpose |
| --- | --- |
| [post_thread.sql](db/queries/post_thread.sql) | All live comments under a post (any depth) |
| [comment_replies.sql](db/queries/comment_replies.sql) | All descendants of a single comment, with vote scores |
| [comment_ancestors.sql](db/queries/comment_ancestors.sql) | Walk a comment up to its post root, with vote scores |
| [delete_comments.sql](db/queries/delete_comments.sql) | Soft-delete a comment subtree |

All four use `WITH RECURSIVE ... CYCLE id SET is_cycle USING PATH` to defend against accidental cycles in the comment graph.

## Repository layer

[repositories/](repositories/) is a thin per-table function module — no ORM, no base class. Each function opens a cursor via `db.connection.get_cursor()` (auto-commit per call via `conn.transaction()`) or delegates to `run_query` for the recursive SQL files.
