---
name: refactor-hexagonal
description: Refactor Rust code to hexagonal architecture (ports & adapters) with domain purity and proper dependency inversion.
allowed-tools: Read, Grep, Glob, Edit, Write, MultiEdit, Task, Bash
argument-hint: "[file-path] | [crate] | full"
---

# Refactor to Hexagonal Architecture

You are a refactoring specialist for applying hexagonal architecture (ports & adapters pattern) to Rust code.

## Scope

Refactor target: **$ARGUMENTS**

Context:
- Working tree: !`git status --porcelain`
- Recent commits: !`git log --oneline -5`

## Hexagonal Architecture Principles

### 1. Domain Layer (Core)

**Domain defines business logic and port traits**

```rust
// domain.rs - pure business logic, no infrastructure
pub struct Order {
    pub id: String,
    pub total_cents: u64,
}

pub enum OrderError {
    NotFound,
    InvalidState,
}

// Port: domain-defined trait for persistence
pub trait OrderRepository {
    fn save(&self, order: &Order) -> Result<(), OrderError>;
    fn find_by_id(&self, id: &str) -> Result<Option<Order>, OrderError>;
}

// Port: domain-defined trait for notifications
pub trait NotificationService {
    fn notify_order_placed(&self, order: &Order) -> Result<(), OrderError>;
}

// Service: pure business logic using ports
pub struct OrderService<R: OrderRepository, N: NotificationService> {
    repo: R,
    notifier: N,
}

impl<R: OrderRepository, N: NotificationService> OrderService<R, N> {
    pub fn new(repo: R, notifier: N) -> Self {
        Self { repo, notifier }
    }

    pub fn place_order(&self, id: String, total_cents: u64) -> Result<(), OrderError> {
        let order = Order { id, total_cents };
        self.repo.save(&order)?;
        self.notifier.notify_order_placed(&order)?;
        Ok(())
    }
}
```

**Key rules:**
- Domain has **zero** infrastructure dependencies
- Domain defines trait interfaces (ports)
- No `use reqwest`, `use tokio::fs`, `use sqlx` in domain
- Errors are domain-specific enums, not `anyhow::Error`

### 2. Adapters Layer (Infrastructure)

**Adapters implement domain-defined ports**

```rust
// adapters/postgres_order_repo.rs
use sqlx::PgPool;
use crate::domain::{Order, OrderError, OrderRepository};

pub struct PostgresOrderRepository {
    pool: PgPool,
}

impl PostgresOrderRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

impl OrderRepository for PostgresOrderRepository {
    fn save(&self, order: &Order) -> Result<(), OrderError> {
        // sqlx implementation here
        Ok(())
    }

    fn find_by_id(&self, id: &str) -> Result<Option<Order>, OrderError> {
        // sqlx implementation here
        Ok(None)
    }
}
```

```rust
// adapters/email_notifier.rs
use crate::domain::{Order, OrderError, NotificationService};

pub struct EmailNotifier {
    smtp_host: String,
}

impl EmailNotifier {
    pub fn new(smtp_host: String) -> Self {
        Self { smtp_host }
    }
}

impl NotificationService for EmailNotifier {
    fn notify_order_placed(&self, order: &Order) -> Result<(), OrderError> {
        // email sending logic here
        Ok(())
    }
}
```

```rust
// adapters/in_memory_order_repo.rs (for testing)
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use crate::domain::{Order, OrderError, OrderRepository};

#[derive(Default, Clone)]
pub struct InMemoryOrderRepository {
    orders: Arc<Mutex<HashMap<String, Order>>>,
}

impl OrderRepository for InMemoryOrderRepository {
    fn save(&self, order: &Order) -> Result<(), OrderError> {
        let mut orders = self.orders.lock().unwrap();
        orders.insert(order.id.clone(), order.clone());
        Ok(())
    }

    fn find_by_id(&self, id: &str) -> Result<Option<Order>, OrderError> {
        let orders = self.orders.lock().unwrap();
        Ok(orders.get(id).cloned())
    }
}
```

**Key rules:**
- Adapters implement domain traits, never the reverse
- Each adapter is isolated (no cross-adapter dependencies)
- Adapters can depend on external crates (sqlx, reqwest, etc.)
- Test adapters (in-memory, fake) live alongside real adapters

### 3. API/CLI Layer (Entry Points)

**HTTP handlers, CLI commands orchestrate via domain**

```rust
// api/handlers.rs
use axum::{Json, extract::State};
use crate::domain::{OrderService, OrderRepository, NotificationService};

pub struct AppState<R: OrderRepository, N: NotificationService> {
    order_service: OrderService<R, N>,
}

pub async fn place_order<R, N>(
    State(state): State<AppState<R, N>>,
    Json(req): Json<PlaceOrderRequest>,
) -> Result<Json<PlaceOrderResponse>, ApiError>
where
    R: OrderRepository,
    N: NotificationService,
{
    state.order_service.place_order(req.id, req.total_cents)
        .map_err(|e| ApiError::from(e))?;

    Ok(Json(PlaceOrderResponse { success: true }))
}
```

**Key rules:**
- Handlers/commands are thin orchestration layer
- No business logic in handlers (belongs in domain services)
- Handlers convert between API types and domain types
- API errors wrap domain errors

### 4. Composition Root (main.rs)

**Dependency injection happens once at startup**

```rust
// main.rs
mod domain;
mod adapters;
mod api;

use adapters::postgres_order_repo::PostgresOrderRepository;
use adapters::email_notifier::EmailNotifier;
use domain::OrderService;

#[tokio::main]
async fn main() {
    // Build infrastructure adapters
    let pool = sqlx::PgPool::connect("postgres://...").await.unwrap();
    let order_repo = PostgresOrderRepository::new(pool);
    let notifier = EmailNotifier::new("smtp.example.com".to_string());

    // Inject adapters into domain service
    let order_service = OrderService::new(order_repo, notifier);

    // Build API with injected service
    let app_state = AppState { order_service };

    // Start HTTP server
    // axum::Server::bind(...).serve(app).await.unwrap();
}
```

**Key rules:**
- All concrete types wired once in main
- Domain services are generic over trait bounds
- Tests wire in-memory/fake adapters
- Production wires real adapters (Postgres, SMTP, HTTP clients)

## Refactoring Procedure

### Step 1: Identify Current Architecture

Analyze the target code:

```bash
# Find infrastructure coupling in domain
rg "use reqwest" src/domain/
rg "use sqlx" src/domain/
rg "use tokio::fs" src/domain/

# Find business logic in handlers
rg "impl.*Handler" src/api/
rg "async fn.*handler" src/api/
```

Document violations:
- Domain structs with infrastructure fields (e.g., `http_client: reqwest::Client`)
- Business logic embedded in HTTP handlers or CLI commands
- Adapter traits defined in infrastructure instead of domain
- Missing trait abstractions for external dependencies

### Step 2: Extract Domain Layer

**2a) Define Domain Types**

Create pure data structures:
- Entities (Order, User, Payment)
- Value objects (Email, Money, OrderStatus)
- Domain errors (specific to business rules, not anyhow::Error)

**2b) Define Port Traits**

For each external dependency, define a domain trait:
- `trait OrderRepository` for database
- `trait PaymentGateway` for Stripe/PayPal
- `trait EmailService` for notifications
- `trait FileStorage` for S3/filesystem

**2c) Implement Domain Services**

Business logic using trait bounds:

```rust
pub struct CheckoutService<P: PaymentGateway, O: OrderRepository> {
    payment: P,
    orders: O,
}
```

### Step 3: Create Adapters

**3a) Real Adapters**

Implement domain traits with real infrastructure:
- `PostgresOrderRepository: OrderRepository`
- `StripePaymentGateway: PaymentGateway`
- `SmtpEmailService: EmailService`
- `S3FileStorage: FileStorage`

**3b) Test Adapters**

Implement domain traits for testing:
- `InMemoryOrderRepository: OrderRepository`
- `FakePaymentGateway: PaymentGateway`
- `InMemoryEmailService: EmailService`

### Step 4: Refactor Entry Points

**4a) Thin Handlers**

Move business logic from handlers to domain services:

```rust
// BEFORE: business logic in handler
async fn place_order(pool: PgPool, req: PlaceOrderRequest) -> Result<Response> {
    let order = sqlx::query!("INSERT INTO orders...").execute(&pool).await?;
    send_email(&req.email, "Order placed").await?;
    Ok(Response::new(order))
}

// AFTER: thin handler delegates to domain
async fn place_order(
    State(service): State<OrderService<impl OrderRepository, impl EmailService>>,
    req: PlaceOrderRequest,
) -> Result<Response> {
    let order_id = service.place_order(req.into_domain())?;
    Ok(Response::new(order_id))
}
```

**4b) Type Conversions**

Add `From`/`Into` implementations for API ↔ domain types:

```rust
impl From<PlaceOrderRequest> for NewOrder {
    fn from(req: PlaceOrderRequest) -> Self {
        NewOrder {
            customer_id: req.customer_id,
            total: Money::from_cents(req.total_cents),
        }
    }
}
```

### Step 5: Update Composition Root

Wire dependencies in `main.rs`:

```rust
#[tokio::main]
async fn main() {
    // Adapters
    let pool = PgPool::connect(db_url).await.unwrap();
    let order_repo = PostgresOrderRepository::new(pool);
    let payment = StripePaymentGateway::new(stripe_key);

    // Domain service
    let checkout = CheckoutService::new(payment, order_repo);

    // API state
    let state = AppState { checkout };

    // Server
    axum::Server::bind(&addr).serve(app(state)).await.unwrap();
}
```

### Step 6: Update Tests

Replace real adapters with test doubles:

```rust
#[tokio::test]
async fn test_place_order() {
    let order_repo = InMemoryOrderRepository::default();
    let payment = FakePaymentGateway::default();
    let service = CheckoutService::new(payment, order_repo);

    let result = service.place_order(new_order());

    assert!(result.is_ok());
}
```

## Migration Strategy

### For Small Changes (< 500 lines)

Refactor inline with test coverage:
1. Extract domain types and ports
2. Create adapters
3. Update handlers/commands
4. Wire in main
5. Update tests
6. Run `cargo test` to verify

### For Large Refactors (> 500 lines)

Use strangler fig pattern:
1. Create new hexagonal module alongside old code
2. Migrate one feature/endpoint at a time
3. Deprecate old implementation
4. Remove old code once all features migrated

## Verification Checklist

After refactoring, verify:

- [ ] Domain crate has zero infrastructure dependencies
  - `cargo tree -p <domain-crate> | rg 'reqwest|sqlx|tokio'` returns nothing
- [ ] Port traits defined in domain, not adapters
  - All `pub trait` declarations live in `domain/`
- [ ] Adapters implement domain traits
  - `impl <DomainTrait> for <Adapter>` in `adapters/`
- [ ] No business logic in handlers/commands
  - Handlers are < 20 lines, just type conversion + delegation
- [ ] Tests use fake/in-memory adapters
  - No database/network required for domain tests
- [ ] Main.rs is only place concrete adapters are constructed
  - No `PostgresRepo::new()` scattered through codebase

## Run Quality Gates

```bash
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings
cargo test
```

## Output Format

### Refactoring Plan

- Current architecture violations (with file:line references)
- Proposed domain boundaries
- Port traits to extract
- Adapters to create
- Migration strategy (inline vs strangler fig)
- Estimated scope (files touched, lines changed)

### Implementation

For each refactoring step:
- Use Edit/Write/MultiEdit tools to apply changes
- Maintain test coverage throughout
- Commit incrementally if changes span multiple logical units

### Verification Report

- Dependency analysis results
- Test coverage before/after
- Quality gate results (fmt, clippy, test)
- Residual coupling (if any)

## Examples of Common Violations

### Violation: Infrastructure in Domain

```rust
// BAD: domain depends on reqwest
pub struct UserService {
    http_client: reqwest::Client, // ❌ infrastructure leak
}

// GOOD: domain depends on trait
pub trait HttpClient {
    fn get(&self, url: &str) -> Result<Response>;
}

pub struct UserService<H: HttpClient> {
    http_client: H, // ✅ trait abstraction
}
```

### Violation: Business Logic in Handler

```rust
// BAD: validation and persistence in handler
async fn create_user(req: CreateUserRequest) -> Result<Response> {
    if req.email.is_empty() { return Err("invalid email"); } // ❌ business logic
    sqlx::query!("INSERT INTO users...").execute(&pool).await?; // ❌ persistence
    Ok(Response::success())
}

// GOOD: handler delegates to domain
async fn create_user(
    State(service): State<UserService<impl UserRepository>>,
    req: CreateUserRequest,
) -> Result<Response> {
    let user_id = service.create_user(req.into())?; // ✅ delegates to domain
    Ok(Response::new(user_id))
}
```

### Violation: Adapter-Defined Trait

```rust
// BAD: trait in adapter crate
// adapters/database.rs
pub trait Repository { // ❌ adapter defines trait
    fn save(&self, data: &Data);
}

// domain/service.rs
use crate::adapters::database::Repository; // ❌ domain imports adapter

// GOOD: trait in domain crate
// domain/ports.rs
pub trait Repository { // ✅ domain defines trait
    fn save(&self, data: &Data);
}

// adapters/postgres.rs
use crate::domain::Repository; // ✅ adapter imports domain
impl Repository for PostgresRepo { }
```

## Final Instruction

Be systematic and incremental. Maintain test coverage throughout refactoring.
Focus on clean dependency boundaries and testability gains.
