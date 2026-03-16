---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--tracing] | [--metrics] | [--full-stack]
description: Setup comprehensive monitoring and observability for Rust applications with tracing, metrics, and logging
---

# Setup Monitoring & Observability

Setup comprehensive observability for Rust applications with tracing crate: **$ARGUMENTS**

## Current Application State

- Rust project: @Cargo.toml (detect dependencies)
- Existing observability: @Cargo.toml (check for tracing, metrics crates)
- Application type: Binary or library detection
- Async runtime: tokio detection

## Task

Implement production-ready observability for Rust with tracing, metrics, and structured logging:

**Observability Type**: Use `--tracing` for distributed tracing, `--metrics` for Prometheus metrics, or `--full-stack` for complete setup

## Rust Observability Stack

### Core Dependencies

Add to `Cargo.toml`:

```toml
[dependencies]
# Tracing framework
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "json", "fmt"] }
tracing-appender = "0.2"

# Metrics
metrics = "0.23"
metrics-exporter-prometheus = "0.15"

# For async tracing
tracing-futures = "0.2"
tokio = { version = "1.48", features = ["full", "tracing"] }

# OpenTelemetry (optional, for distributed tracing)
opentelemetry = { version = "0.24", features = ["trace", "metrics"] }
opentelemetry-otlp = "0.17"
opentelemetry_sdk = { version = "0.24", features = ["rt-tokio"] }
tracing-opentelemetry = "0.25"
```

## Tracing Setup

### Basic Tracing Configuration

```rust
// src/observability/tracing.rs
use tracing::{info, warn, error, debug, trace};
use tracing_subscriber::{
    fmt,
    layer::SubscriberExt,
    util::SubscriberInitExt,
    EnvFilter,
};

pub fn init_tracing() {
    tracing_subscriber::registry()
        .with(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info,my_app=debug".into())
        )
        .with(fmt::layer())
        .init();

    info!("Tracing initialized");
}
```

### Structured JSON Logging

```rust
// src/observability/logging.rs
use tracing_subscriber::{fmt, prelude::*, EnvFilter};
use tracing_appender::non_blocking;
use std::io;

pub fn init_structured_logging() {
    let (non_blocking_stdout, _guard) = non_blocking(io::stdout());

    tracing_subscriber::registry()
        .with(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info".into())
        )
        .with(
            fmt::layer()
                .json()
                .with_writer(non_blocking_stdout)
                .with_current_span(true)
                .with_span_list(true)
        )
        .init();
}
```

### File Logging with Rotation

```rust
// src/observability/file_logging.rs
use tracing_subscriber::{fmt, prelude::*, EnvFilter};
use tracing_appender::rolling;

pub fn init_file_logging() {
    let file_appender = rolling::daily("./logs", "app.log");
    let (non_blocking, _guard) = tracing_appender::non_blocking(file_appender);

    tracing_subscriber::registry()
        .with(EnvFilter::from_default_env())
        .with(
            fmt::layer()
                .json()
                .with_writer(non_blocking)
        )
        .init();
}
```

### Tracing in Application Code

```rust
// src/main.rs
use tracing::{info, warn, error, instrument, Span};

#[instrument]
async fn process_request(user_id: u64, request_id: String) -> Result<(), Error> {
    info!("Processing request");

    // Add custom fields to current span
    Span::current().record("user_id", user_id);

    let result = fetch_data(user_id).await?;

    info!(
        result_count = result.len(),
        "Request processed successfully"
    );

    Ok(())
}

#[instrument(skip(db))]
async fn fetch_data(user_id: u64) -> Result<Vec<Data>, Error> {
    info!("Fetching data from database");
    // Database call
    Ok(vec![])
}
```

## Metrics Setup

### Prometheus Metrics Configuration

```rust
// src/observability/metrics.rs
use metrics::{counter, gauge, histogram, describe_counter, describe_gauge, describe_histogram};
use metrics_exporter_prometheus::{Matcher, PrometheusBuilder, PrometheusHandle};
use std::time::Duration;

pub fn init_metrics() -> PrometheusHandle {
    // Describe metrics
    describe_counter!("http_requests_total", "Total number of HTTP requests");
    describe_histogram!("http_request_duration_seconds", "HTTP request duration in seconds");
    describe_gauge!("active_connections", "Number of active connections");

    // Configure buckets for histograms
    PrometheusBuilder::new()
        .set_buckets_for_metric(
            Matcher::Full("http_request_duration_seconds".to_string()),
            &[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
        )
        .expect("Failed to set buckets")
        .install_recorder()
        .expect("Failed to install Prometheus recorder")
}

pub fn record_http_request(method: &str, path: &str, status: u16, duration: Duration) {
    let labels = [
        ("method", method.to_string()),
        ("path", path.to_string()),
        ("status", status.to_string()),
    ];

    counter!("http_requests_total", &labels).increment(1);
    histogram!("http_request_duration_seconds", &labels).record(duration.as_secs_f64());
}

pub fn update_active_connections(count: i64) {
    gauge!("active_connections").set(count as f64);
}
```

### Metrics HTTP Endpoint (Axum)

```rust
// src/routes/metrics.rs
use axum::{response::IntoResponse, routing::get, Router};
use metrics_exporter_prometheus::PrometheusHandle;

pub fn metrics_routes(handle: PrometheusHandle) -> Router {
    Router::new().route("/metrics", get(move || async move {
        handle.render()
    }))
}
```

### Application Metrics Middleware

```rust
// src/middleware/metrics.rs
use axum::{
    extract::Request,
    middleware::Next,
    response::Response,
};
use std::time::Instant;

pub async fn metrics_middleware(
    req: Request,
    next: Next,
) -> Response {
    let start = Instant::now();
    let method = req.method().to_string();
    let path = req.uri().path().to_string();

    let response = next.run(req).await;

    let duration = start.elapsed();
    let status = response.status().as_u16();

    crate::observability::metrics::record_http_request(
        &method,
        &path,
        status,
        duration,
    );

    response
}
```

## OpenTelemetry Integration

### Distributed Tracing with OTLP

```rust
// src/observability/otel.rs
use opentelemetry::{global, KeyValue};
use opentelemetry_otlp::WithExportConfig;
use opentelemetry_sdk::{
    runtime,
    trace::{self, RandomIdGenerator, Sampler},
    Resource,
};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

pub fn init_opentelemetry(service_name: &str, otlp_endpoint: &str) -> Result<(), Box<dyn std::error::Error>> {
    let tracer = opentelemetry_otlp::new_pipeline()
        .tracing()
        .with_exporter(
            opentelemetry_otlp::new_exporter()
                .tonic()
                .with_endpoint(otlp_endpoint)
        )
        .with_trace_config(
            trace::config()
                .with_sampler(Sampler::AlwaysOn)
                .with_id_generator(RandomIdGenerator::default())
                .with_resource(Resource::new(vec![
                    KeyValue::new("service.name", service_name.to_string()),
                    KeyValue::new("service.version", env!("CARGO_PKG_VERSION")),
                ]))
        )
        .install_batch(runtime::Tokio)?;

    // Create tracing layer
    let telemetry = tracing_opentelemetry::layer().with_tracer(tracer);

    tracing_subscriber::registry()
        .with(EnvFilter::from_default_env())
        .with(telemetry)
        .init();

    Ok(())
}

pub fn shutdown_opentelemetry() {
    global::shutdown_tracer_provider();
}
```

## Complete Application Setup

```rust
// src/main.rs
mod observability;
mod middleware;
mod routes;

use axum::{
    middleware as axum_middleware,
    routing::get,
    Router,
};
use std::net::SocketAddr;
use tracing::info;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize observability
    observability::tracing::init_tracing();
    let metrics_handle = observability::metrics::init_metrics();

    info!("Starting application");

    // Build application
    let app = Router::new()
        .route("/", get(handler))
        .merge(routes::metrics::metrics_routes(metrics_handle))
        .layer(axum_middleware::from_fn(middleware::metrics::metrics_middleware))
        .layer(tower_http::trace::TraceLayer::new_for_http());

    // Run server
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    info!("Listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

#[tracing::instrument]
async fn handler() -> &'static str {
    info!("Handling request");
    "Hello, World!"
}
```

## Structured Logging Patterns

### Request Context Logging

```rust
use tracing::{info_span, Instrument};
use uuid::Uuid;

async fn handle_request(req: Request) -> Response {
    let request_id = Uuid::new_v4().to_string();

    async {
        info!("Processing request");
        // Request handling logic
    }
    .instrument(info_span!(
        "http_request",
        request_id = %request_id,
        method = %req.method(),
        path = %req.uri().path(),
    ))
    .await
}
```

### Error Logging with Context

```rust
use tracing::{error, warn};

async fn process_data(data: Data) -> Result<(), AppError> {
    data.validate().map_err(|e| {
        error!(
            error = %e,
            data_id = %data.id,
            "Data validation failed"
        );
        e
    })?;

    database::save(&data).await.map_err(|e| {
        error!(
            error = %e,
            data_id = %data.id,
            "Failed to save data to database"
        );
        e
    })?;

    Ok(())
}
```

## Environment Configuration

### Environment Variables

```bash
# .env
RUST_LOG=info,my_app=debug,tower_http=debug
OTLP_ENDPOINT=http://localhost:4317
METRICS_PORT=9090
```

### Configuration File

```rust
// src/config.rs
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct ObservabilityConfig {
    pub log_level: String,
    pub log_format: LogFormat,
    pub metrics_enabled: bool,
    pub tracing_enabled: bool,
    pub otlp_endpoint: Option<String>,
}

#[derive(Debug, Deserialize)]
pub enum LogFormat {
    Json,
    Pretty,
}
```

## Docker Integration

### docker-compose.yml with Observability Stack

```yaml
version: '3.8'

services:
  app:
    build: .
    environment:
      - RUST_LOG=info
      - OTLP_ENDPOINT=http://jaeger:4317
    ports:
      - "8080:8080"
      - "9090:9090"  # Metrics endpoint
    depends_on:
      - jaeger
      - prometheus

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9091:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true

volumes:
  prometheus-data:
  grafana-data:
```

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rust-app'
    static_configs:
      - targets: ['app:9090']
        labels:
          service: 'my-rust-app'
```

## Best Practices

1. **Use `#[instrument]` macro** - Automatically create spans for functions
2. **Structured logging** - Use JSON format in production
3. **Log levels** - Use appropriate levels (error, warn, info, debug, trace)
4. **Context propagation** - Include request IDs and user context
5. **Metrics naming** - Follow Prometheus naming conventions
6. **Sampling** - Use sampling for high-traffic applications
7. **Performance** - Use `non_blocking` writers for file logging
8. **Security** - Don't log sensitive data (passwords, tokens)

## Health Check Endpoint

```rust
// src/routes/health.rs
use axum::{http::StatusCode, Json};
use serde::Serialize;

#[derive(Serialize)]
struct HealthResponse {
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

## Output

Complete observability setup with:
- Tracing framework with structured logging
- Prometheus metrics integration
- OpenTelemetry distributed tracing
- JSON logging for production
- File logging with rotation
- HTTP metrics middleware
- Health check endpoints
- Docker Compose observability stack
- Grafana dashboards
- Jaeger trace visualization

**Monitoring Stack:**
- Application: tracing + metrics crates
- Collection: Prometheus
- Visualization: Grafana
- Distributed Tracing: Jaeger with OTLP
