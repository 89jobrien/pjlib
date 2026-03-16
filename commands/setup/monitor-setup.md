---
argument-hint: [--prometheus] | [--full-stack]
description: Setup monitoring infrastructure with Prometheus, Grafana, and alerting for Rust applications
---

# Monitoring and Observability Setup

Setup comprehensive monitoring infrastructure for Rust applications: **$ARGUMENTS**

## Context

Implement production-ready monitoring with Prometheus metrics, Grafana dashboards, and alerting for Rust services.

## Current State

Confirm the working directory before outlining monitoring steps.

!`pwd`

## Rust Metrics Setup

### Application Instrumentation

```rust
// src/metrics.rs
use metrics::{counter, histogram, gauge};
use metrics_exporter_prometheus::PrometheusBuilder;
use std::time::Duration;

pub fn init_metrics() -> metrics_exporter_prometheus::PrometheusHandle {
    PrometheusBuilder::new()
        .set_buckets_for_metric(
            metrics_exporter_prometheus::Matcher::Full("http_request_duration_seconds".to_string()),
            &[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
        )
        .unwrap()
        .install_recorder()
        .unwrap()
}

// Record HTTP request metrics
pub fn record_request(method: &str, path: &str, status: u16, duration: Duration) {
    counter!(
        "http_requests_total",
        "method" => method.to_string(),
        "path" => path.to_string(),
        "status" => status.to_string(),
    ).increment(1);

    histogram!(
        "http_request_duration_seconds",
        "method" => method.to_string(),
        "path" => path.to_string(),
    ).record(duration.as_secs_f64());
}

// Record application metrics
pub fn record_db_query(query_type: &str, duration: Duration) {
    histogram!(
        "db_query_duration_seconds",
        "query_type" => query_type.to_string(),
    ).record(duration.as_secs_f64());
}

pub fn set_active_connections(count: i64) {
    gauge!("active_connections").set(count as f64);
}
```

### Axum Metrics Middleware

```rust
// src/middleware/metrics.rs
use axum::{extract::Request, middleware::Next, response::Response};
use std::time::Instant;

pub async fn track_metrics(req: Request, next: Next) -> Response {
    let start = Instant::now();
    let method = req.method().clone();
    let path = req.uri().path().to_string();

    let response = next.run(req).await;
    let duration = start.elapsed();
    let status = response.status();

    crate::metrics::record_request(
        method.as_str(),
        &path,
        status.as_u16(),
        duration,
    );

    response
}
```

## Prometheus Configuration

### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    region: 'us-east-1'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'rust-api'
    static_configs:
      - targets: ['app:9090']
        labels:
          service: 'api'
          environment: 'production'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

## Alert Rules

### alerts/application.yml

```yaml
groups:
  - name: rust_application
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
          / sum(rate(http_requests_total[5m])) by (service) > 0.05
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate on {{ $labels.service }}"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # Slow response time
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          ) > 1.0
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "Slow response time on {{ $labels.service }}"
          description: "P95 latency is {{ $value }}s (threshold: 1s)"

      # High database latency
      - alert: HighDatabaseLatency
        expr: |
          histogram_quantile(0.99,
            sum(rate(db_query_duration_seconds_bucket[5m])) by (le, query_type)
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database latency for {{ $labels.query_type }}"

      # Service down
      - alert: ServiceDown
        expr: up{job="rust-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"

  - name: infrastructure
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: |
          100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"

      # High memory usage
      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
```

## Grafana Dashboard

### Rust Application Dashboard JSON

```json
{
  "dashboard": {
    "title": "Rust API Metrics",
    "uid": "rust-api",
    "tags": ["rust", "api"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "targets": [{
          "expr": "sum(rate(http_requests_total[5m])) by (method)",
          "legendFormat": "{{method}}"
        }]
      },
      {
        "title": "Error Rate %",
        "type": "graph",
        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
        "targets": [{
          "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
          "legendFormat": "Error %"
        }]
      },
      {
        "title": "Response Time (P50, P95, P99)",
        "type": "graph",
        "gridPos": {"x": 0, "y": 8, "w": 24, "h": 8},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "p99"
          }
        ]
      }
    ]
  }
}
```

## Docker Compose Setup

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts:/etc/prometheus/alerts
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'

volumes:
  prometheus-data:
  grafana-data:
```

## Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: pagerduty
      continue: true
    - match_re:
        severity: critical|warning
      receiver: slack

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://localhost:5001/'

  - name: 'slack'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        description: '{{ .GroupLabels.alertname }}: {{ .Annotations.summary }}'
```

## Output Format

1. **Metrics Implementation**: Rust application instrumented with metrics crate
2. **Prometheus Setup**: Complete Prometheus configuration with scrape configs
3. **Grafana Dashboards**: Pre-built dashboards for Rust applications
4. **Alert Rules**: Comprehensive alerting for errors, latency, and infrastructure
5. **Alertmanager**: Multi-channel alert routing (Slack, PagerDuty)
6. **Docker Compose**: Complete monitoring stack deployment

This monitoring system provides full observability into Rust application performance with automatic alerting for critical issues.
