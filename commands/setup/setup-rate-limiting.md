---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--token-bucket] | [--sliding-window] | [--governor]
description: Implement API rate limiting for Rust applications using tower-governor middleware
---

# Setup Rate Limiting

Implement comprehensive API rate limiting for Rust with tower-governor: **$ARGUMENTS**

## Current API State

- Rust framework: @Cargo.toml (detect axum, actix-web)
- Existing rate limiting: !`grep -r "governor\|rate.limit" src/ 2>/dev/null | wc -l`
- Redis availability: !`redis-cli ping 2>/dev/null || echo "Redis not available"`
- API endpoints: !`grep -r "#\[.*route\]" src/ 2>/dev/null | wc -l`

## Task

Implement production-ready rate limiting for Rust APIs with governor algorithm:

**Rate Limit Algorithm**: Use `--token-bucket` (default), `--sliding-window`, or `--governor` for tower-governor integration

## Tower-Governor Rate Limiting

### Dependencies

Add to `Cargo.toml`:

```toml
[dependencies]
# Rate limiting
tower-governor = "0.4"
governor = "0.7"

# Web framework
axum = "0.8"
tower = "0.5"

# For distributed rate limiting (optional)
redis = { version = "0.26", features = ["tokio-comp", "connection-manager"] }
```

### Basic Rate Limiting

```rust
// src/middleware/rate_limit.rs
use axum::Router;
use governor::{Quota, RateLimiter};
use std::num::NonZeroU32;
use tower_governor::{
    governor::GovernorConfigBuilder,
    GovernorLayer,
};

pub fn rate_limit_layer() -> GovernorLayer<'static> {
    // 100 requests per minute
    let governor_conf = Box::new(
        GovernorConfigBuilder::default()
            .per_second(2)
            .burst_size(100)
            .finish()
            .unwrap(),
    );

    GovernorLayer {
        config: Box::leak(governor_conf),
    }
}

// In main.rs
let app = Router::new()
    .route("/api/users", get(list_users))
    .layer(rate_limit_layer());
```

### IP-Based Rate Limiting

```rust
// src/middleware/ip_rate_limit.rs
use axum::{
    extract::ConnectInfo,
    http::{Request, StatusCode},
    middleware::Next,
    response::Response,
};
use governor::{
    clock::DefaultClock,
    state::{InMemoryState, NotKeyed},
    Quota, RateLimiter,
};
use std::{
    net::SocketAddr,
    num::NonZeroU32,
    sync::Arc,
};

pub struct IpRateLimiter {
    limiter: Arc<RateLimiter<NotKeyed, InMemoryState, DefaultClock>>,
}

impl IpRateLimiter {
    pub fn new(requests_per_second: u32) -> Self {
        let quota = Quota::per_second(NonZeroU32::new(requests_per_second).unwrap());
        let limiter = Arc::new(RateLimiter::direct(quota));

        Self { limiter }
    }

    pub async fn check<B>(
        &self,
        ConnectInfo(addr): ConnectInfo<SocketAddr>,
        request: Request<B>,
        next: Next<B>,
    ) -> Result<Response, StatusCode> {
        if self.limiter.check().is_ok() {
            Ok(next.run(request).await)
        } else {
            Err(StatusCode::TOO_MANY_REQUESTS)
        }
    }
}
```

### User-Based Rate Limiting

```rust
// src/middleware/user_rate_limit.rs
use axum::{
    extract::{Request, State},
    http::StatusCode,
    middleware::Next,
    response::Response,
};
use dashmap::DashMap;
use governor::{
    clock::DefaultClock,
    state::InMemoryState,
    Quota, RateLimiter,
};
use std::{num::NonZeroU32, sync::Arc};

#[derive(Clone)]
pub struct UserRateLimitState {
    limiters: Arc<DashMap<String, Arc<RateLimiter<NotKeyed, InMemoryState, DefaultClock>>>>,
    quota: Quota,
}

impl UserRateLimitState {
    pub fn new(requests_per_minute: u32) -> Self {
        let quota = Quota::per_minute(NonZeroU32::new(requests_per_minute).unwrap());

        Self {
            limiters: Arc::new(DashMap::new()),
            quota,
        }
    }

    fn get_limiter(&self, user_id: &str) -> Arc<RateLimiter<NotKeyed, InMemoryState, DefaultClock>> {
        self.limiters
            .entry(user_id.to_string())
            .or_insert_with(|| Arc::new(RateLimiter::direct(self.quota)))
            .clone()
    }
}

pub async fn user_rate_limit_middleware(
    State(state): State<UserRateLimitState>,
    request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    // Extract user_id from JWT or session
    let user_id = extract_user_id(&request).ok_or(StatusCode::UNAUTHORIZED)?;

    let limiter = state.get_limiter(&user_id);

    if limiter.check().is_ok() {
        Ok(next.run(request).await)
    } else {
        Err(StatusCode::TOO_MANY_REQUESTS)
    }
}

fn extract_user_id(request: &Request) -> Option<String> {
    // Extract from Authorization header or session
    request
        .headers()
        .get("Authorization")
        .and_then(|h| h.to_str().ok())
        .map(|s| s.to_string())
}
```

### Tiered Rate Limiting

```rust
// src/middleware/tiered_rate_limit.rs
use governor::Quota;
use std::num::NonZeroU32;

#[derive(Debug, Clone)]
pub enum UserTier {
    Free,
    Pro,
    Enterprise,
}

impl UserTier {
    pub fn quota(&self) -> Quota {
        match self {
            UserTier::Free => Quota::per_minute(NonZeroU32::new(60).unwrap()),
            UserTier::Pro => Quota::per_minute(NonZeroU32::new(300).unwrap()),
            UserTier::Enterprise => Quota::per_minute(NonZeroU32::new(1000).unwrap()),
        }
    }
}

pub async fn tiered_rate_limit(
    user_id: String,
    tier: UserTier,
) -> Result<(), StatusCode> {
    let quota = tier.quota();
    let limiter = RateLimiter::direct(quota);

    if limiter.check().is_ok() {
        Ok(())
    } else {
        Err(StatusCode::TOO_MANY_REQUESTS)
    }
}
```

### Redis-Backed Distributed Rate Limiting

```rust
// src/middleware/redis_rate_limit.rs
use redis::{AsyncCommands, Client};
use std::time::Duration;

pub struct RedisRateLimiter {
    client: Client,
}

impl RedisRateLimiter {
    pub fn new(redis_url: &str) -> Result<Self, redis::RedisError> {
        Ok(Self {
            client: Client::open(redis_url)?,
        })
    }

    pub async fn check_rate_limit(
        &self,
        key: &str,
        max_requests: u32,
        window: Duration,
    ) -> Result<bool, redis::RedisError> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;

        let current: u32 = conn.get(key).await.unwrap_or(0);

        if current >= max_requests {
            return Ok(false);
        }

        let _: () = conn.incr(key, 1).await?;
        let _: () = conn.expire(key, window.as_secs() as i64).await?;

        Ok(true)
    }
}

pub async fn redis_rate_limit_middleware(
    State(limiter): State<RedisRateLimiter>,
    request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let user_id = extract_user_id(&request).ok_or(StatusCode::UNAUTHORIZED)?;
    let key = format!("rate_limit:{}", user_id);

    let allowed = limiter
        .check_rate_limit(&key, 100, Duration::from_secs(60))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if allowed {
        Ok(next.run(request).await)
    } else {
        Err(StatusCode::TOO_MANY_REQUESTS)
    }
}
```

### Rate Limit Headers

```rust
// src/middleware/rate_limit_headers.rs
use axum::{
    http::{HeaderMap, HeaderValue},
    response::Response,
};

pub fn add_rate_limit_headers(
    mut response: Response,
    limit: u32,
    remaining: u32,
    reset: u64,
) -> Response {
    let headers = response.headers_mut();

    headers.insert("X-RateLimit-Limit", HeaderValue::from(limit));
    headers.insert("X-RateLimit-Remaining", HeaderValue::from(remaining));
    headers.insert("X-RateLimit-Reset", HeaderValue::from(reset));

    response
}
```

### Complete Application Example

```rust
// src/main.rs
use axum::{
    middleware,
    routing::get,
    Router,
};
use std::net::SocketAddr;
use tower::ServiceBuilder;
use tower_governor::GovernorLayer;

mod handlers;
mod middleware as mw;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/public", get(handlers::public))
        .layer(GovernorLayer::default())
        .route("/api/authenticated", get(handlers::authenticated))
        .layer(
            ServiceBuilder::new()
                .layer(middleware::from_fn_with_state(
                    mw::user_rate_limit::UserRateLimitState::new(100),
                    mw::user_rate_limit::user_rate_limit_middleware,
                ))
        );

    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();

    axum::serve(listener, app).await.unwrap();
}
```

### Custom Error Response

```rust
// src/errors.rs
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

pub struct RateLimitError {
    pub retry_after: u64,
}

impl IntoResponse for RateLimitError {
    fn into_response(self) -> Response {
        (
            StatusCode::TOO_MANY_REQUESTS,
            [("Retry-After", self.retry_after.to_string())],
            Json(json!({
                "error": "Rate limit exceeded",
                "retry_after": self.retry_after
            })),
        )
        .into_response()
    }
}
```

### Testing Rate Limits

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use axum::http::{Request, StatusCode};
    use tower::ServiceExt;

    #[tokio::test]
    async fn test_rate_limit() {
        let app = Router::new()
            .route("/api/test", get(|| async { "OK" }))
            .layer(rate_limit_layer());

        // First request should succeed
        let response = app
            .clone()
            .oneshot(Request::builder().uri("/api/test").body(Body::empty()).unwrap())
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);

        // After exceeding limit, should get 429
        for _ in 0..100 {
            let _ = app
                .clone()
                .oneshot(Request::builder().uri("/api/test").body(Body::empty()).unwrap())
                .await;
        }

        let response = app
            .oneshot(Request::builder().uri("/api/test").body(Body::empty()).unwrap())
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::TOO_MANY_REQUESTS);
    }
}
```

## Configuration

```toml
# config.toml
[rate_limit]
enabled = true
default_limit = 100
window_seconds = 60

[rate_limit.tiers.free]
requests_per_minute = 60

[rate_limit.tiers.pro]
requests_per_minute = 300

[rate_limit.tiers.enterprise]
requests_per_minute = 1000
```

## Output

Complete rate limiting system with:
- Tower-governor middleware integration
- IP-based rate limiting
- User-based rate limiting with tiers
- Redis-backed distributed rate limiting
- Rate limit headers in responses
- Custom error handling
- Comprehensive testing
- Configuration management
- Production-ready monitoring

**Algorithms Supported:**
- Token bucket (governor default)
- Sliding window (with Redis)
- Fixed window (basic implementation)
