---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--development] | [--production] | [--compose]
description: Setup Docker containerization for Rust applications with multi-stage builds and optimized images
---

# Setup Docker Containers

Setup comprehensive Docker containerization for Rust applications: **$ARGUMENTS**

## Current Project State

- Rust project: @Cargo.toml (detect binary or library)
- Existing Docker: @Dockerfile or @docker-compose.yml (if exists)
- Cargo workspace: @Cargo.toml with [workspace] section
- Binary targets: !`grep "\[\[bin\]\]" Cargo.toml | wc -l` binaries

## Task

Implement production-ready Docker containerization for Rust with multi-stage builds and optimized images:

**Environment Type**: Use `--development` for dev setup, `--production` for optimized builds, or `--compose` for multi-service setup

## Multi-Stage Dockerfile for Rust

### Production Dockerfile (Optimized)

Create `Dockerfile`:

```dockerfile
# Rust Builder Stage
FROM rust:1.75-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Copy source tree
COPY src ./src

# Build for release
RUN cargo build --release --locked

# Runtime Stage
FROM debian:bookworm-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy binary from builder
COPY --from=builder /app/target/release/my-app /usr/local/bin/my-app

# Switch to non-root user
USER appuser

# Expose port (adjust as needed)
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/my-app"]
```

### Workspace Dockerfile

For Cargo workspaces with multiple binaries:

```dockerfile
# Builder Stage
FROM rust:1.75-slim-bookworm AS builder

RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy workspace manifests
COPY Cargo.toml Cargo.lock ./
COPY crates/*/Cargo.toml ./crates/

# Copy all source
COPY crates ./crates

# Build all workspace members
RUN cargo build --workspace --release --locked

# Runtime Stage for specific binary
FROM debian:bookworm-slim AS runtime

RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

# Copy specific binary (adjust name)
COPY --from=builder /app/target/release/api /usr/local/bin/api

USER appuser
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/api"]
```

### Optimized Build with Layer Caching

```dockerfile
# Chef Stage - Cache dependencies
FROM rust:1.75-slim-bookworm AS chef

RUN cargo install cargo-chef
WORKDIR /app

# Planner Stage
FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# Builder Stage
FROM chef AS builder

COPY --from=planner /app/recipe.json recipe.json

# Build dependencies - this layer is cached
RUN cargo chef cook --release --recipe-path recipe.json

# Build application
COPY . .
RUN cargo build --release --locked

# Runtime Stage
FROM debian:bookworm-slim AS runtime

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

COPY --from=builder /app/target/release/my-app /usr/local/bin/my-app

USER appuser
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/my-app"]
```

### Distroless Image (Smallest Size)

```dockerfile
# Builder
FROM rust:1.75-slim AS builder

WORKDIR /app
COPY . .

RUN cargo build --release --locked

# Runtime using distroless
FROM gcr.io/distroless/cc-debian12

COPY --from=builder /app/target/release/my-app /app

EXPOSE 8080
ENTRYPOINT ["/app"]
```

### Alpine-based (Small Image)

```dockerfile
# Builder
FROM rust:1.75-alpine AS builder

RUN apk add --no-cache musl-dev

WORKDIR /app
COPY . .

# Build static binary
RUN cargo build --release --target x86_64-unknown-linux-musl --locked

# Runtime
FROM alpine:3.19

RUN apk add --no-cache ca-certificates

COPY --from=builder /app/target/x86_64-unknown-linux-musl/release/my-app /usr/local/bin/my-app

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/my-app"]
```

## Docker Compose for Development

### Development Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
      target: development
    volumes:
      - .:/app
      - cargo-cache:/usr/local/cargo/registry
      - target-cache:/app/target
    environment:
      - RUST_LOG=debug
      - RUST_BACKTRACE=1
      - DATABASE_URL=postgres://postgres:password@postgres:5432/myapp
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  cargo-cache:
  target-cache:
  postgres-data:
  redis-data:
```

### Development Dockerfile

Create `Dockerfile.dev`:

```dockerfile
FROM rust:1.75-slim-bookworm AS development

RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install cargo-watch for hot reloading
RUN cargo install cargo-watch

WORKDIR /app

# Development mode: source is mounted as volume
CMD ["cargo", "watch", "-x", "run"]
```

## Advanced Patterns

### Multi-Platform Builds

```dockerfile
# Support both amd64 and arm64
FROM --platform=$BUILDPLATFORM rust:1.75-slim AS builder

ARG TARGETPLATFORM
ARG BUILDPLATFORM

WORKDIR /app
COPY . .

# Cross-compile based on target platform
RUN case "$TARGETPLATFORM" in \
    "linux/amd64") TARGET=x86_64-unknown-linux-gnu ;; \
    "linux/arm64") TARGET=aarch64-unknown-linux-gnu ;; \
    esac && \
    cargo build --release --target $TARGET --locked

FROM debian:bookworm-slim
# Copy appropriate binary based on platform
```

### Health Checks

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# In docker-compose.yml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

### Build Arguments and Secrets

```dockerfile
# Use build arguments
ARG RUST_VERSION=1.75
FROM rust:${RUST_VERSION}-slim AS builder

# Use build secrets (requires BuildKit)
RUN --mount=type=secret,id=cargo_token \
    CARGO_REGISTRY_TOKEN=$(cat /run/secrets/cargo_token) \
    cargo build --release
```

Build with:
```bash
docker build --secret id=cargo_token,src=$HOME/.cargo/credentials .
```

## .dockerignore

Create `.dockerignore`:

```
# Git
.git
.gitignore

# Rust
target/
**/*.rs.bk
*.pdb

# IDE
.idea/
.vscode/
*.swp

# CI
.github/

# Documentation
README.md
docs/

# Tests
tests/fixtures/

# Environment
.env
.env.local
```

## Docker Commands

### Building

```bash
# Build production image
docker build -t my-app:latest .

# Build with BuildKit (faster)
DOCKER_BUILDKIT=1 docker build -t my-app:latest .

# Build specific stage
docker build --target builder -t my-app:builder .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t my-app:latest .
```

### Running

```bash
# Run container
docker run -p 8080:8080 my-app:latest

# Run with environment variables
docker run -p 8080:8080 -e DATABASE_URL=postgres://... my-app:latest

# Run with volume mount (development)
docker run -p 8080:8080 -v $(pwd):/app my-app:dev

# Run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f app
```

### Optimization

```bash
# Check image size
docker images my-app

# Analyze layers
docker history my-app:latest

# Dive tool for layer analysis
dive my-app:latest

# Remove unused images
docker image prune -a
```

## GitHub Actions Integration

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Best Practices

1. **Multi-stage builds** - Separate builder and runtime stages
2. **Layer caching** - Use cargo-chef for dependency caching
3. **Minimal base images** - Use slim, alpine, or distroless images
4. **Non-root user** - Always run as non-root for security
5. **Health checks** - Implement health check endpoints
6. **BuildKit** - Use DOCKER_BUILDKIT=1 for faster builds
7. **Secrets management** - Use build secrets, not ARGs
8. **Static linking** - Use musl for fully static binaries
9. **.dockerignore** - Exclude unnecessary files
10. **Security scanning** - Use trivy or grype for vulnerability scanning

## Security Scanning

```bash
# Scan with Trivy
trivy image my-app:latest

# Scan with Grype
grype my-app:latest

# Scan in CI
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image my-app:latest
```

## Output

Complete Docker setup with:
- Multi-stage Dockerfile for optimized builds
- Development Docker Compose setup
- Production-ready container images
- Layer caching with cargo-chef
- Security best practices (non-root user, minimal images)
- Health checks and monitoring
- CI/CD integration for automated builds
- Multi-platform support (amd64, arm64)

**Image Size Comparison:**
- Full rust image: ~1.5GB
- Debian slim runtime: ~100-200MB
- Alpine runtime: ~20-50MB
- Distroless runtime: ~10-30MB
