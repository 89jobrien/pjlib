---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--postgres] | [--sqlite] | [--mysql]
description: Design optimized database schemas for Rust applications using SQLx with migrations and type safety
---

# Design Database Schema

Design optimized database schemas for Rust with SQLx: **$ARGUMENTS**

## Current Project Context

- Rust project: @Cargo.toml (detect sqlx, diesel)
- Existing schema: !`find . -name "*.sql" -path "*/migrations/*" | wc -l` migrations
- Database type: @Cargo.toml (detect postgres, mysql, sqlite features)
- Application requirements: Based on project analysis

## Current State

Confirm repository context before drafting schema.

!`pwd`

## Task

Design comprehensive database schema with SQLx and compile-time query verification:

**Database Type**: Use `--postgres` (recommended), `--sqlite`, or `--mysql`

## SQLx Database Design

### Dependencies

Add to `Cargo.toml`:

```toml
[dependencies]
# Database
sqlx = { version = "0.8", features = ["runtime-tokio", "tls-rustls", "postgres", "chrono", "uuid"] }

# For migrations
sqlx = { version = "0.8", features = ["migrate"] }

# Types
chrono = { version = "0.4", features = ["serde"] }
uuid = { version = "1.11", features = ["v4", "serde"] }
```

### Installation

```bash
# Install SQLx CLI
cargo install sqlx-cli --no-default-features --features postgres

# Create database
sqlx database create

# Create migration
sqlx migrate add create_users_table
```

### Schema Design Example

#### Users Table Migration

```sql
-- migrations/20240101000001_create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Posts Table with Relationships

```sql
-- migrations/20240101000002_create_posts_table.sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_published ON posts(published);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Tags and Many-to-Many Relationship

```sql
-- migrations/20240101000003_create_tags_and_post_tags.sql
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE post_tags (
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (post_id, tag_id)
);

CREATE INDEX idx_post_tags_post_id ON post_tags(post_id);
CREATE INDEX idx_post_tags_tag_id ON post_tags(tag_id);
```

### Rust Models

```rust
// src/models/user.rs
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct User {
    pub id: i64,
    pub email: String,
    pub username: String,
    #[serde(skip_serializing)]
    pub password_hash: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Deserialize)]
pub struct CreateUser {
    pub email: String,
    pub username: String,
    pub password: String,
}

#[derive(Debug, Deserialize)]
pub struct UpdateUser {
    pub email: Option<String>,
    pub username: Option<String>,
}
```

### Database Repository

```rust
// src/db/users.rs
use sqlx::PgPool;
use crate::models::user::{User, CreateUser, UpdateUser};

pub struct UserRepository {
    pool: PgPool,
}

impl UserRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    pub async fn create(&self, user: &CreateUser) -> Result<User, sqlx::Error> {
        let user = sqlx::query_as!(
            User,
            r#"
            INSERT INTO users (email, username, password_hash)
            VALUES ($1, $2, $3)
            RETURNING id, email, username, password_hash, created_at, updated_at
            "#,
            user.email,
            user.username,
            user.password, // Should be hashed in production
        )
        .fetch_one(&self.pool)
        .await?;

        Ok(user)
    }

    pub async fn find_by_id(&self, id: i64) -> Result<Option<User>, sqlx::Error> {
        let user = sqlx::query_as!(
            User,
            r#"SELECT * FROM users WHERE id = $1"#,
            id
        )
        .fetch_optional(&self.pool)
        .await?;

        Ok(user)
    }

    pub async fn find_by_email(&self, email: &str) -> Result<Option<User>, sqlx::Error> {
        let user = sqlx::query_as!(
            User,
            r#"SELECT * FROM users WHERE email = $1"#,
            email
        )
        .fetch_optional(&self.pool)
        .await?;

        Ok(user)
    }

    pub async fn list(&self, limit: i64, offset: i64) -> Result<Vec<User>, sqlx::Error> {
        let users = sqlx::query_as!(
            User,
            r#"
            SELECT * FROM users
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            "#,
            limit,
            offset
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(users)
    }

    pub async fn update(&self, id: i64, user: &UpdateUser) -> Result<User, sqlx::Error> {
        let updated = sqlx::query_as!(
            User,
            r#"
            UPDATE users
            SET email = COALESCE($1, email),
                username = COALESCE($2, username)
            WHERE id = $3
            RETURNING *
            "#,
            user.email,
            user.username,
            id
        )
        .fetch_one(&self.pool)
        .await?;

        Ok(updated)
    }

    pub async fn delete(&self, id: i64) -> Result<(), sqlx::Error> {
        sqlx::query!("DELETE FROM users WHERE id = $1", id)
            .execute(&self.pool)
            .await?;

        Ok(())
    }
}
```

### Database Transactions

```rust
// src/db/transactions.rs
use sqlx::{PgPool, Postgres, Transaction};

pub async fn create_user_with_posts(
    pool: &PgPool,
    user: &CreateUser,
    posts: Vec<CreatePost>,
) -> Result<(User, Vec<Post>), sqlx::Error> {
    let mut tx: Transaction<Postgres> = pool.begin().await?;

    // Create user
    let user = sqlx::query_as!(
        User,
        "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
        user.email,
        user.username,
        user.password
    )
    .fetch_one(&mut *tx)
    .await?;

    // Create posts
    let mut created_posts = Vec::new();
    for post in posts {
        let created_post = sqlx::query_as!(
            Post,
            "INSERT INTO posts (user_id, title, content) VALUES ($1, $2, $3) RETURNING *",
            user.id,
            post.title,
            post.content
        )
        .fetch_one(&mut *tx)
        .await?;

        created_posts.push(created_post);
    }

    tx.commit().await?;

    Ok((user, created_posts))
}
```

### Database Testing

```rust
// tests/db_tests.rs
use sqlx::PgPool;

#[sqlx::test]
async fn test_create_user(pool: PgPool) -> sqlx::Result<()> {
    let repo = UserRepository::new(pool);

    let user = CreateUser {
        email: "test@example.com".to_string(),
        username: "testuser".to_string(),
        password: "hashedpassword".to_string(),
    };

    let created = repo.create(&user).await?;

    assert_eq!(created.email, user.email);
    assert_eq!(created.username, user.username);

    Ok(())
}

#[sqlx::test]
async fn test_find_by_email(pool: PgPool) -> sqlx::Result<()> {
    let repo = UserRepository::new(pool);

    // Create user first
    let user = CreateUser {
        email: "test@example.com".to_string(),
        username: "testuser".to_string(),
        password: "hashedpassword".to_string(),
    };

    repo.create(&user).await?;

    // Find by email
    let found = repo.find_by_email("test@example.com").await?;

    assert!(found.is_some());
    assert_eq!(found.unwrap().email, user.email);

    Ok(())
}
```

### Advanced Patterns

#### Soft Deletes

```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
```

```rust
pub async fn soft_delete(&self, id: i64) -> Result<(), sqlx::Error> {
    sqlx::query!(
        "UPDATE users SET deleted_at = NOW() WHERE id = $1",
        id
    )
    .execute(&self.pool)
    .await?;

    Ok(())
}

pub async fn list_active(&self) -> Result<Vec<User>, sqlx::Error> {
    sqlx::query_as!(
        User,
        "SELECT * FROM users WHERE deleted_at IS NULL"
    )
    .fetch_all(&self.pool)
    .await
}
```

#### Full-Text Search

```sql
ALTER TABLE posts ADD COLUMN search_vector tsvector;

CREATE INDEX idx_posts_search ON posts USING gin(search_vector);

CREATE TRIGGER posts_search_vector_update BEFORE INSERT OR UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);
```

```rust
pub async fn search_posts(&self, query: &str) -> Result<Vec<Post>, sqlx::Error> {
    sqlx::query_as!(
        Post,
        r#"
        SELECT * FROM posts
        WHERE search_vector @@ plainto_tsquery('english', $1)
        ORDER BY ts_rank(search_vector, plainto_tsquery('english', $1)) DESC
        "#,
        query
    )
    .fetch_all(&self.pool)
    .await
}
```

## Running Migrations

```bash
# Run migrations
sqlx migrate run

# Revert last migration
sqlx migrate revert

# Check migration status
sqlx migrate info
```

## Output

Complete database schema with:
- SQLx migrations with version control
- Type-safe queries with compile-time verification
- Repository pattern implementation
- Transaction support
- Database testing with `#[sqlx::test]`
- Advanced patterns (soft deletes, full-text search)
- Indexing strategies
- Relationship modeling
- Performance optimization

**Best Practices:**
- Use prepared statements (automatic with SQLx)
- Add indexes on foreign keys and frequently queried columns
- Use transactions for multi-step operations
- Implement soft deletes for auditing
- Use UUID for distributed systems
- Add timestamps for audit trails
