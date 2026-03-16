---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--rest] | [--websocket] | [--graphql]
description: Implement REST API with axum framework, including JSON endpoints, middleware, and WebSocket support
---

# Implement REST API

Implement comprehensive REST API using axum framework: **$ARGUMENTS**

## Current Application Context

- Rust project: @Cargo.toml (detect dependencies)
- Existing API: !`find . -name "*.rs" -path "*/routes/*" | wc -l` route files
- Database integration: @Cargo.toml (detect sqlx, diesel)
- Async runtime: tokio detection

## Task

Build production-ready REST API with axum framework and comprehensive features:

**API Type**: Use `--rest` for standard REST API, `--websocket` for WebSocket support, or `--graphql` for GraphQL with async-graphql

## Axum REST API Implementation

### Dependencies

Add to `Cargo.toml`:

```toml
[dependencies]
# Web framework
axum = { version = "0.8", features = ["macros", "ws"] }
tower = "0.5"
tower-http = { version = "0.6", features = ["trace", "cors", "compression"] }

# Async runtime
tokio = { version = "1.48", features = ["full"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Validation
validator = { version = "0.18", features = ["derive"] }

# Error handling
anyhow = "1.0"
thiserror = "2.0"

# Observability
tracing = "0.1"
```

### Project Structure

```
src/
├── main.rs
├── routes/
│   ├── mod.rs
│   ├── users.rs
│   ├── health.rs
│   └── api_v1.rs
├── handlers/
│   ├── mod.rs
│   └── users.rs
├── models/
│   ├── mod.rs
│   └── user.rs
├── middleware/
│   ├── mod.rs
│   ├── auth.rs
│   └── logging.rs
└── errors.rs
```

### Basic Axum Application

```rust
// src/main.rs
use axum::{
    routing::{get, post},
    Router,
};
use std::net::SocketAddr;
use tower_http::{
    cors::CorsLayer,
    trace::TraceLayer,
    compression::CompressionLayer,
};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

mod routes;
mod handlers;
mod models;
mod middleware;
mod errors;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info,my_api=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Build application with routes
    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(handlers::health::health_check))
        .nest("/api/v1", routes::api_v1::routes())
        .layer(CorsLayer::permissive())
        .layer(CompressionLayer::new())
        .layer(TraceLayer::new_for_http());

    // Run server
    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    tracing::info!("Listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn root() -> &'static str {
    "Welcome to the API"
}
```

### Models with Validation

```rust
// src/models/user.rs
use serde::{Deserialize, Serialize};
use validator::Validate;

#[derive(Debug, Serialize, Deserialize)]
pub struct User {
    pub id: i64,
    pub name: String,
    pub email: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(length(min = 1, max = 100))]
    pub name: String,

    #[validate(email)]
    pub email: String,
}

#[derive(Debug, Deserialize)]
pub struct UpdateUserRequest {
    #[validate(length(min = 1, max = 100))]
    pub name: Option<String>,

    #[validate(email)]
    pub email: Option<String>,
}
```

### Handlers with State

```rust
// src/handlers/users.rs
use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use validator::Validate;

use crate::{
    models::user::{CreateUserRequest, User},
    errors::ApiError,
};

pub async fn list_users(
    State(pool): State<sqlx::PgPool>,
) -> Result<Json<Vec<User>>, ApiError> {
    let users = sqlx::query_as!(User, "SELECT * FROM users")
        .fetch_all(&pool)
        .await?;

    Ok(Json(users))
}

pub async fn get_user(
    State(pool): State<sqlx::PgPool>,
    Path(id): Path<i64>,
) -> Result<Json<User>, ApiError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_one(&pool)
        .await?;

    Ok(Json(user))
}

pub async fn create_user(
    State(pool): State<sqlx::PgPool>,
    Json(payload): Json<CreateUserRequest>,
) -> Result<(StatusCode, Json<User>), ApiError> {
    // Validate input
    payload.validate()?;

    let user = sqlx::query_as!(
        User,
        "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
        payload.name,
        payload.email
    )
    .fetch_one(&pool)
    .await?;

    Ok((StatusCode::CREATED, Json(user)))
}

pub async fn delete_user(
    State(pool): State<sqlx::PgPool>,
    Path(id): Path<i64>,
) -> Result<StatusCode, ApiError> {
    sqlx::query!("DELETE FROM users WHERE id = $1", id)
        .execute(&pool)
        .await?;

    Ok(StatusCode::NO_CONTENT)
}
```

### Error Handling

```rust
// src/errors.rs
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

#[derive(Debug)]
pub enum ApiError {
    DatabaseError(sqlx::Error),
    ValidationError(validator::ValidationErrors),
    NotFound,
}

impl From<sqlx::Error> for ApiError {
    fn from(err: sqlx::Error) -> Self {
        ApiError::DatabaseError(err)
    }
}

impl From<validator::ValidationErrors> for ApiError {
    fn from(err: validator::ValidationErrors) -> Self {
        ApiError::ValidationError(err)
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            ApiError::DatabaseError(sqlx::Error::RowNotFound) => {
                (StatusCode::NOT_FOUND, "Resource not found".to_string())
            }
            ApiError::DatabaseError(err) => {
                tracing::error!("Database error: {:?}", err);
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error".to_string())
            }
            ApiError::ValidationError(err) => {
                (StatusCode::BAD_REQUEST, format!("Validation error: {}", err))
            }
            ApiError::NotFound => {
                (StatusCode::NOT_FOUND, "Resource not found".to_string())
            }
        };

        (status, Json(json!({ "error": message }))).into_response()
    }
}
```

### Routes

```rust
// src/routes/api_v1.rs
use axum::{
    routing::{get, post},
    Router,
};
use crate::handlers;

pub fn routes() -> Router<sqlx::PgPool> {
    Router::new()
        .route("/users", get(handlers::users::list_users))
        .route("/users", post(handlers::users::create_user))
        .route("/users/:id", get(handlers::users::get_user))
        .route("/users/:id", delete(handlers::users::delete_user))
}
```

### Authentication Middleware

```rust
// src/middleware/auth.rs
use axum::{
    extract::Request,
    http::{HeaderMap, StatusCode},
    middleware::Next,
    response::Response,
};

pub async fn auth_middleware(
    headers: HeaderMap,
    request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let auth_header = headers
        .get("Authorization")
        .and_then(|h| h.to_str().ok())
        .ok_or(StatusCode::UNAUTHORIZED)?;

    if !auth_header.starts_with("Bearer ") {
        return Err(StatusCode::UNAUTHORIZED);
    }

    let token = &auth_header[7..];

    // Validate token (example - replace with actual JWT validation)
    if token != "valid-token" {
        return Err(StatusCode::UNAUTHORIZED);
    }

    Ok(next.run(request).await)
}
```

### WebSocket Support

```rust
// src/routes/websocket.rs
use axum::{
    extract::{ws::{Message, WebSocket}, WebSocketUpgrade},
    response::Response,
};
use futures::{sink::SinkExt, stream::StreamExt};

pub async fn ws_handler(ws: WebSocketUpgrade) -> Response {
    ws.on_upgrade(handle_socket)
}

async fn handle_socket(socket: WebSocket) {
    let (mut sender, mut receiver) = socket.split();

    while let Some(msg) = receiver.next().await {
        if let Ok(msg) = msg {
            match msg {
                Message::Text(text) => {
                    tracing::info!("Received: {}", text);
                    if sender.send(Message::Text(format!("Echo: {}", text))).await.is_err() {
                        break;
                    }
                }
                Message::Close(_) => break,
                _ => {}
            }
        }
    }
}
```

### Health Check

```rust
// src/handlers/health.rs
use axum::{http::StatusCode, Json};
use serde::Serialize;

#[derive(Serialize)]
pub struct HealthResponse {
    status: String,
    version: String,
}

pub async fn health_check() -> (StatusCode, Json<HealthResponse>) {
    (
        StatusCode::OK,
        Json(HealthResponse {
            status: "healthy".to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
        }),
    )
}
```

### CORS Configuration

```rust
use tower_http::cors::{Any, CorsLayer};

let cors = CorsLayer::new()
    .allow_origin(Any)
    .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE])
    .allow_headers([header::CONTENT_TYPE, header::AUTHORIZATION]);

let app = Router::new()
    .route("/api/v1/users", get(list_users))
    .layer(cors);
```

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use axum::{
        body::Body,
        http::{Request, StatusCode},
    };
    use tower::ServiceExt;

    #[tokio::test]
    async fn test_health_check() {
        let app = Router::new().route("/health", get(health_check));

        let response = app
            .oneshot(Request::builder().uri("/health").body(Body::empty()).unwrap())
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);
    }
}
```

## Output

Complete REST API with:
- Axum framework with routing and handlers
- JSON serialization with serde
- Input validation with validator
- Error handling with custom error types
- Authentication middleware
- WebSocket support
- CORS configuration
- Health check endpoints
- Comprehensive testing
- Structured logging with tracing

**Note**: This replaces GraphQL-focused content with Rust's axum REST API framework, which aligns with the Maestro project's architecture.
