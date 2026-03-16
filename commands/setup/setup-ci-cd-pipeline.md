---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [--github-actions] | [--gitlab-ci]
description: Setup comprehensive CI/CD pipeline for Rust projects with automated testing, linting, and deployment
---

# Setup CI/CD Pipeline

Setup comprehensive Rust CI/CD pipeline with GitHub Actions: **$ARGUMENTS**

## Current Repository State

- Version control: !`git remote -v | head -1` (GitHub, GitLab, etc.)
- Existing CI: !`find . -name ".github" -o -name ".gitlab-ci.yml" | wc -l`
- Cargo workspace: @Cargo.toml with [workspace] section
- Test files: !`find . -name "*.rs" -path "*/tests/*" | wc -l` integration tests

## Task

Implement production-ready CI/CD pipeline for Rust projects with comprehensive automation:

**Platform Choice**: Use `--github-actions` (default) or `--gitlab-ci` for GitLab CI

**Pipeline Architecture**:

1. **Build Automation** - Rust compilation, dependency caching, parallel builds
2. **Testing Strategy** - Unit tests, integration tests, doc tests, code coverage
3. **Quality Gates** - Clippy linting, rustfmt formatting, security audits
4. **Performance** - Benchmarking, build time optimization, test sharding
5. **Deployment** - Binary artifacts, Docker images, crate publishing
6. **Matrix Builds** - Multiple Rust versions, platforms, feature combinations

## GitHub Actions CI/CD Pipeline

### Complete Workflow (Maestro-style)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

env:
  CARGO_TERM_COLOR: always
  RUST_BACKTRACE: 1

jobs:
  # Job 1: Code formatting check
  format:
    name: Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt

      - name: Check formatting
        run: cargo fmt --all -- --check

  # Job 2: Linting with clippy
  clippy:
    name: Clippy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy

      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "clippy"

      - name: Run clippy
        run: cargo clippy --workspace --all-targets --all-features --locked -- -D warnings

  # Job 3: Build
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable

      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "build"

      - name: Build workspace
        run: cargo build --workspace --all-features --locked

      - name: Build release
        run: cargo build --workspace --all-features --locked --release

  # Job 4: Tests
  test:
    name: Test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        rust: [stable, beta]
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@master
        with:
          toolchain: ${{ matrix.rust }}

      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "test-${{ matrix.os }}-${{ matrix.rust }}"

      - uses: taiki-e/install-action@nextest

      - name: Run tests
        run: cargo nextest run --workspace --all-features --locked

      - name: Run doc tests
        run: cargo test --workspace --doc --locked

  # Job 5: Code coverage
  coverage:
    name: Coverage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable

      - uses: Swatinem/rust-cache@v2

      - uses: taiki-e/install-action@cargo-llvm-cov
      - uses: taiki-e/install-action@nextest

      - name: Generate coverage
        run: cargo llvm-cov nextest --workspace --all-features --lcov --output-path lcov.info

      - name: Upload to codecov
        uses: codecov/codecov-action@v3
        with:
          files: lcov.info
          fail_ci_if_error: true

  # Job 6: Security audit
  audit:
    name: Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable

      - uses: rustsec/audit-check@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

  # Job 7: Dependency check
  dependencies:
    name: Dependencies
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable

      - name: Check Cargo.lock is up to date
        run: cargo check --workspace --locked

      - name: Install cargo-outdated
        run: cargo install cargo-outdated

      - name: Check for outdated dependencies
        run: cargo outdated --workspace --exit-code 1
        continue-on-error: true
```

### Advanced Features

#### Test Sharding (Parallel Tests)

```yaml
test-shard:
  name: Test (Shard ${{ matrix.shard }})
  runs-on: ubuntu-latest
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:
    - uses: actions/checkout@v4
    - uses: dtolnay/rust-toolchain@stable
    - uses: Swatinem/rust-cache@v2
    - uses: taiki-e/install-action@nextest

    - name: Run tests (shard ${{ matrix.shard }}/4)
      run: |
        cargo nextest run \
          --workspace \
          --partition count:${{ matrix.shard }}/4
```

#### Benchmarking

```yaml
benchmark:
  name: Benchmark
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: dtolnay/rust-toolchain@stable
    - uses: Swatinem/rust-cache@v2

    - name: Run benchmarks
      run: cargo bench --workspace

    - name: Store benchmark result
      uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'cargo'
        output-file-path: target/criterion/output.json
        github-token: ${{ secrets.GITHUB_TOKEN }}
        auto-push: true
```

#### Docker Build and Push

```yaml
docker:
  name: Docker Build & Push
  runs-on: ubuntu-latest
  needs: [test, clippy]
  if: github.ref == 'refs/heads/main'
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

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}:latest
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### Crate Publishing

```yaml
publish:
  name: Publish to crates.io
  runs-on: ubuntu-latest
  needs: [test, clippy, audit]
  if: startsWith(github.ref, 'refs/tags/v')
  steps:
    - uses: actions/checkout@v4

    - uses: dtolnay/rust-toolchain@stable

    - name: Publish to crates.io
      run: cargo publish --token ${{ secrets.CARGO_TOKEN }}
      env:
        CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_TOKEN }}
```

### Cargo Caching Strategies

```yaml
# Strategy 1: Simple caching (Swatinem/rust-cache)
- uses: Swatinem/rust-cache@v2
  with:
    shared-key: "build"      # Share cache between jobs
    cache-on-failure: true   # Cache even if job fails
    workspaces: |
      . -> target
      crates/foo -> crates/foo/target

# Strategy 2: Manual caching
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/bin/
      ~/.cargo/registry/index/
      ~/.cargo/registry/cache/
      ~/.cargo/git/db/
      target/
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-
```

### Environment-Specific Configurations

```yaml
deploy-staging:
  name: Deploy to Staging
  runs-on: ubuntu-latest
  needs: [test, clippy]
  if: github.ref == 'refs/heads/main'
  environment:
    name: staging
    url: https://staging.example.com
  steps:
    - uses: actions/checkout@v4
    - uses: dtolnay/rust-toolchain@stable
    - uses: Swatinem/rust-cache@v2

    - name: Build release binary
      run: cargo build --release --bin api

    - name: Deploy to staging
      run: |
        # Upload binary to staging server
        scp target/release/api deploy@staging.example.com:/opt/app/
        ssh deploy@staging.example.com 'systemctl restart app'
      env:
        SSH_KEY: ${{ secrets.STAGING_SSH_KEY }}
```

## GitLab CI Pipeline

Create `.gitlab-ci.yml`:

```yaml
variables:
  CARGO_HOME: ${CI_PROJECT_DIR}/.cargo
  RUST_BACKTRACE: "1"

stages:
  - check
  - test
  - build
  - deploy

cache:
  paths:
    - .cargo/
    - target/

format:
  stage: check
  image: rust:latest
  script:
    - rustup component add rustfmt
    - cargo fmt --all -- --check

clippy:
  stage: check
  image: rust:latest
  script:
    - rustup component add clippy
    - cargo clippy --workspace --all-targets --all-features --locked -- -D warnings

test:
  stage: test
  image: rust:latest
  script:
    - cargo install cargo-nextest
    - cargo nextest run --workspace --all-features --locked
  parallel:
    matrix:
      - RUST_VERSION: ["stable", "beta", "nightly"]
  image: rust:${RUST_VERSION}

coverage:
  stage: test
  image: rust:latest
  script:
    - cargo install cargo-llvm-cov cargo-nextest
    - cargo llvm-cov nextest --workspace --all-features --lcov --output-path lcov.info
  artifacts:
    paths:
      - lcov.info
    reports:
      coverage_report:
        coverage_format: cobertura
        path: lcov.info

build:
  stage: build
  image: rust:latest
  script:
    - cargo build --workspace --release --locked
  artifacts:
    paths:
      - target/release/
    expire_in: 1 week

audit:
  stage: check
  image: rust:latest
  script:
    - cargo install cargo-audit
    - cargo audit
  allow_failure: true
```

## Additional Configuration Files

### Cargo.toml CI/CD Settings

```toml
# Workspace Cargo.toml
[profile.ci]
inherits = "dev"
debug = false        # Faster builds
incremental = false  # Better for CI

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
```

### .cargo/config.toml

```toml
[build]
jobs = 4

[term]
color = "always"

[net]
git-fetch-with-cli = true  # Better for CI
```

### Dependabot Configuration

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "your-team"
    labels:
      - "dependencies"
      - "rust"
```

## CI/CD Best Practices

1. **Always use `--locked` flag** - Ensures reproducible builds
2. **Cache dependencies** - Use `Swatinem/rust-cache` or similar
3. **Parallel jobs** - Run lint, test, build in parallel
4. **Matrix builds** - Test on multiple OS and Rust versions
5. **Security audit** - Run `cargo audit` on every PR
6. **Code coverage** - Track coverage with `cargo-llvm-cov`
7. **Benchmark tracking** - Monitor performance regressions
8. **Fail fast** - Stop on first failure to save CI time

## Performance Optimization

```yaml
# Use sparse registry for faster dependency resolution
env:
  CARGO_REGISTRIES_CRATES_IO_PROTOCOL: sparse

# Use sccache for compilation caching
- uses: mozilla-actions/sccache-action@v0.0.3
- env:
    RUSTC_WRAPPER: sccache
    SCCACHE_GHA_ENABLED: "true"
```

## Output

Complete CI/CD pipeline with:
- Automated linting and formatting checks
- Comprehensive testing (unit, integration, doc tests)
- Code coverage reporting
- Security vulnerability scanning
- Multi-platform builds
- Deployment automation
- Dependency caching for faster builds
- Matrix testing across Rust versions and OS platforms

**Verification**:

```bash
# Test CI configuration locally with act
act -j test

# Verify GitHub Actions syntax
gh workflow view ci.yml
```
