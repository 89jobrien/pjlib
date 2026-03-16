# DevLoop Architecture Patterns

Quick reference for common architectural patterns in DevLoop.

## Hexagonal Architecture Overview

```
┌─────────────────────────────────────────┐
│  Primary Adapters (UI/CLI)              │
│  - Ratatui TUI (crates/cli)             │
│  - Non-interactive CLI (devloop-cli)    │
│  - WebSocket relay (relay)              │
└───────────────┬─────────────────────────┘
                │
                │ Application Ports (traits)
                ▼
┌─────────────────────────────────────────┐
│  Application Core (components)          │
│  - Domain models (domain.rs)            │
│  - Ports: TimelineProvider,             │
│           BranchAggregator,             │
│           InsightProvider               │
│  - Pure business logic                  │
└───────────────┬─────────────────────────┘
                │
                │ Infrastructure Ports (traits)
                ▼
┌─────────────────────────────────────────┐
│  Secondary Adapters (Infrastructure)    │
│  - GitAdapter (git2)                    │
│  - BamlAdapter (AI)                     │
│  - GkgAdapter (code structure)          │
│  - CouncilAdapter (multi-role AI)       │
│  - UnifiedAdapter (composition)         │
└─────────────────────────────────────────┘
```

## Pattern 1: Domain Model Design

**Rule:** Domain models have ZERO external dependencies.

**Good Example:**

```rust
// crates/components/src/domain.rs
use std::collections::HashMap; // std only!

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BranchSummary {
    pub name: String,
    pub commit_count: usize,
    pub session_count: usize,
    pub first_activity: String,
    pub last_activity: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BranchInsight {
    pub branch_name: String,
    pub health_score: f64,
    pub risk_level: RiskLevel,
    pub insights: Vec<String>,
    pub recommendations: Vec<String>,
    pub analyst_role: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RiskLevel {
    Low,
    Medium,
    High,
}
```

**Bad Example:**

```rust
// DON'T DO THIS - external dependency in domain!
use serde_json::Value; // External dep
use git2::Repository;   // Infrastructure concern

pub struct BranchSummary {
    pub repo: Repository, // ❌ Couples domain to git2
    pub data: Value,      // ❌ Couples domain to serde_json
}
```

## Pattern 2: Port Definition (Trait-Based)

**Rule:** Define ports as traits with async methods returning domain types.

**Example:**

```rust
// crates/components/src/ports.rs
use async_trait::async_trait;
use crate::domain::{BranchSummary, TimelineEntry, BranchInsight};

#[async_trait]
pub trait BranchAggregator: Send + Sync {
    async fn get_branch_summary(&self, branch_name: &str) -> Result<BranchSummary, String>;
    async fn list_branches(&self) -> Result<Vec<BranchSummary>, String>;
}

#[async_trait]
pub trait TimelineProvider: Send + Sync {
    async fn get_timeline(&self, branch_name: &str) -> Result<Vec<TimelineEntry>, String>;
}

#[async_trait]
pub trait InsightProvider: Send + Sync {
    async fn analyze_branch(&self, branch_name: &str) -> Result<BranchInsight, String>;
    async fn analyze_council(&self, branch_name: &str) -> Result<Vec<BranchInsight>, String>;
}
```

**Why async_trait?**
- Enables async methods in traits (stable Rust async fn in traits is still evolving)
- Required for `Send + Sync` bounds on async trait methods

## Pattern 3: Adapter Implementation

**Rule:** Adapters implement traits and handle external dependencies.

**Example:**

```rust
// crates/cli/src/adapters/git.rs
use async_trait::async_trait;
use git2::Repository;
use devloop_components::ports::BranchAggregator;
use devloop_components::domain::BranchSummary;

pub struct GitAdapter {
    repo: Repository,
    claude_projects_dir: PathBuf,
}

impl GitAdapter {
    pub fn new(repo_path: &Path) -> Result<Self, String> {
        let repo = Repository::open(repo_path)
            .map_err(|e| format!("Failed to open repo: {}", e))?;

        let claude_projects_dir = dirs::home_dir()
            .ok_or("No home directory")?
            .join(".claude/projects");

        Ok(Self { repo, claude_projects_dir })
    }
}

#[async_trait]
impl BranchAggregator for GitAdapter {
    async fn get_branch_summary(&self, branch_name: &str) -> Result<BranchSummary, String> {
        // Implementation using git2 crate
        // Returns pure domain type (BranchSummary)
        todo!()
    }

    async fn list_branches(&self) -> Result<Vec<BranchSummary>, String> {
        // Implementation
        todo!()
    }
}
```

## Pattern 4: Dependency Injection

**Rule:** App is generic over adapters, receives trait objects.

**Example:**

```rust
// crates/cli/src/app.rs
pub struct App<T, B, I>
where
    T: TimelineProvider,
    B: BranchAggregator,
    I: InsightProvider,
{
    timeline_provider: Arc<T>,
    branch_aggregator: Arc<B>,
    insight_provider: Arc<I>,
    view_state: ViewState,
}

impl<T, B, I> App<T, B, I>
where
    T: TimelineProvider + 'static,
    B: BranchAggregator + 'static,
    I: InsightProvider + 'static,
{
    pub fn new(
        timeline_provider: Arc<T>,
        branch_aggregator: Arc<B>,
        insight_provider: Arc<I>,
    ) -> Self {
        Self {
            timeline_provider,
            branch_aggregator,
            insight_provider,
            view_state: ViewState::BranchList,
        }
    }

    pub async fn load_branches(&mut self) -> Result<(), String> {
        let branches = self.branch_aggregator.list_branches().await?;
        self.view_state = ViewState::BranchList(branches);
        Ok(())
    }
}
```

**Main function:**

```rust
// crates/cli/src/main.rs
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let repo_path = std::env::current_dir()?;

    // Create adapters
    let git_adapter = Arc::new(GitAdapter::new(&repo_path)?);
    let baml_adapter = Arc::new(BamlAdapter::new()?);
    let unified = Arc::new(UnifiedAdapter::new(
        git_adapter.clone(),
        baml_adapter.clone(),
    ));

    // Inject dependencies
    let mut app = App::new(
        unified.clone(), // TimelineProvider
        unified.clone(), // BranchAggregator
        unified,         // InsightProvider
    );

    app.run().await?;
    Ok(())
}
```

## Pattern 5: Adapter Composition

**Rule:** Compose multiple adapters into unified interface.

**Example:**

```rust
// crates/cli/src/adapters/unified.rs
pub struct UnifiedAdapter {
    git: Arc<GitAdapter>,
    baml: Arc<BamlAdapter>,
    gkg: Option<Arc<GkgAdapter>>,
}

impl UnifiedAdapter {
    pub fn new(git: Arc<GitAdapter>, baml: Arc<BamlAdapter>) -> Self {
        let gkg = GkgAdapter::new().ok().map(Arc::new);

        if gkg.is_none() {
            eprintln!("Warning: GKG adapter unavailable, falling back to git-only mode");
        }

        Self { git, baml, gkg }
    }
}

#[async_trait]
impl TimelineProvider for UnifiedAdapter {
    async fn get_timeline(&self, branch_name: &str) -> Result<Vec<TimelineEntry>, String> {
        // Delegate to git adapter
        self.git.get_timeline(branch_name).await
    }
}

#[async_trait]
impl InsightProvider for UnifiedAdapter {
    async fn analyze_branch(&self, branch_name: &str) -> Result<BranchInsight, String> {
        // Get git data
        let summary = self.git.get_branch_summary(branch_name).await?;

        // Optionally enrich with GKG data
        let code_structure = if let Some(gkg) = &self.gkg {
            gkg.get_repo_map().await.ok()
        } else {
            None
        };

        // Delegate to BAML for analysis
        self.baml.analyze_with_context(summary, code_structure).await
    }
}
```

## Pattern 6: Test Doubles

**Rule:** Create test doubles by implementing traits, no mocking framework needed.

**Example:**

```rust
// crates/cli/tests/test_doubles.rs
pub struct MockBranchAggregator {
    branches: Vec<BranchSummary>,
}

impl MockBranchAggregator {
    pub fn with_branches(branches: Vec<BranchSummary>) -> Self {
        Self { branches }
    }
}

#[async_trait]
impl BranchAggregator for MockBranchAggregator {
    async fn get_branch_summary(&self, branch_name: &str) -> Result<BranchSummary, String> {
        self.branches
            .iter()
            .find(|b| b.name == branch_name)
            .cloned()
            .ok_or_else(|| format!("Branch not found: {}", branch_name))
    }

    async fn list_branches(&self) -> Result<Vec<BranchSummary>, String> {
        Ok(self.branches.clone())
    }
}

// Use in tests
#[tokio::test]
async fn test_app_loads_branches() {
    let mock_branches = vec![
        BranchSummary {
            name: "feature/test".to_string(),
            commit_count: 3,
            session_count: 1,
            first_activity: "2026-03-10".to_string(),
            last_activity: "2026-03-15".to_string(),
        },
    ];

    let mock_aggregator = Arc::new(MockBranchAggregator::with_branches(mock_branches));
    let mock_timeline = Arc::new(MockTimelineProvider::empty());
    let mock_insights = Arc::new(MockInsightProvider::empty());

    let mut app = App::new(mock_timeline, mock_aggregator, mock_insights);

    app.load_branches().await.unwrap();

    // Assert app state
}
```

## Pattern 7: BAML Integration

**Rule:** BAML adapter wraps generated client, maps to domain types.

**Example:**

```rust
// crates/cli/src/adapters/baml.rs
use baml_client::baml_types::BranchInsight as BamlBranchInsight;
use devloop_components::domain::BranchInsight;

pub struct BamlAdapter {
    client: baml_client::BamlClient,
}

impl BamlAdapter {
    pub fn new() -> Result<Self, String> {
        let client = baml_client::BamlClient::new();
        Ok(Self { client })
    }

    async fn analyze_with_role(
        &self,
        branch_name: &str,
        commits: &str,
        sessions: &str,
        commit_count: i64,
        session_count: i64,
        role: AnalystRole,
    ) -> Result<BranchInsight, String> {
        let baml_result = match role {
            AnalystRole::StrictCritic => {
                self.client
                    .analyze_branch_strict_critic(branch_name, commits, sessions, commit_count, session_count)
                    .await
            }
            AnalystRole::CreativeExplorer => {
                self.client
                    .analyze_branch_creative_explorer(branch_name, commits, sessions, commit_count, session_count)
                    .await
            }
            // ... other roles
        };

        let baml_insight = baml_result.map_err(|e| format!("BAML error: {}", e))?;

        // Map BAML type to domain type
        Ok(BranchInsight {
            branch_name: baml_insight.branch_name,
            health_score: baml_insight.health_score,
            risk_level: map_risk_level(baml_insight.risk_level),
            insights: baml_insight.insights,
            recommendations: baml_insight.recommendations,
            analyst_role: format!("{:?}", role),
        })
    }
}

fn map_risk_level(baml_level: String) -> RiskLevel {
    match baml_level.to_lowercase().as_str() {
        "low" => RiskLevel::Low,
        "medium" => RiskLevel::Medium,
        "high" => RiskLevel::High,
        _ => RiskLevel::Medium, // Default
    }
}
```

## Pattern 8: Error Handling

**Rule:** Adapters return domain-level errors (String or custom error type), not infrastructure errors.

**Example:**

```rust
// Good: Maps infrastructure error to domain error
impl GitAdapter {
    async fn get_commits(&self, branch_name: &str) -> Result<Vec<Commit>, String> {
        let branch_ref = self.repo
            .find_branch(branch_name, git2::BranchType::Local)
            .map_err(|e| format!("Branch not found: {}", e))?; // ✅ Map to String

        // ... rest of implementation
        Ok(commits)
    }
}

// Bad: Leaks infrastructure error
impl GitAdapter {
    async fn get_commits(&self, branch_name: &str) -> Result<Vec<Commit>, git2::Error> {
        let branch_ref = self.repo
            .find_branch(branch_name, git2::BranchType::Local)?; // ❌ Leaks git2::Error

        Ok(commits)
    }
}
```

## Pattern 9: Graceful Degradation

**Rule:** Optional adapters should fail gracefully, not crash the app.

**Example:**

```rust
// UnifiedAdapter with optional GKG
pub struct UnifiedAdapter {
    git: Arc<GitAdapter>,
    baml: Arc<BamlAdapter>,
    gkg: Option<Arc<GkgAdapter>>, // Optional!
}

impl UnifiedAdapter {
    pub fn new(git: Arc<GitAdapter>, baml: Arc<BamlAdapter>) -> Self {
        let gkg = match GkgAdapter::new() {
            Ok(adapter) => {
                println!("GKG adapter initialized successfully");
                Some(Arc::new(adapter))
            }
            Err(e) => {
                eprintln!("Warning: GKG unavailable ({}), continuing without code structure data", e);
                None
            }
        };

        Self { git, baml, gkg }
    }

    async fn get_code_structure(&self, path: &str) -> Option<CodeStructure> {
        match &self.gkg {
            Some(gkg) => gkg.get_structure(path).await.ok(),
            None => None, // Gracefully return None
        }
    }
}
```

## Pattern 10: Council Pattern (Multi-Perspective Analysis)

**Rule:** Run multiple analysts in parallel, aggregate results.

**Example:**

```rust
// crates/cli/src/adapters/council.rs
pub struct CouncilAdapter {
    baml: Arc<BamlAdapter>,
}

impl CouncilAdapter {
    pub fn new(baml: Arc<BamlAdapter>) -> Self {
        Self { baml }
    }
}

#[async_trait]
impl InsightProvider for CouncilAdapter {
    async fn analyze_council(&self, branch_name: &str) -> Result<Vec<BranchInsight>, String> {
        let summary = self.get_branch_summary(branch_name).await?;

        // Define council roles
        let roles = vec![
            AnalystRole::StrictCritic,
            AnalystRole::CreativeExplorer,
            AnalystRole::GeneralAnalyst,
            AnalystRole::SecurityReviewer,
            AnalystRole::PerformanceAnalyst,
        ];

        // Run analyses in parallel
        let futures = roles.into_iter().map(|role| {
            let baml = self.baml.clone();
            let summary = summary.clone();
            async move {
                baml.analyze_with_role(
                    &summary.name,
                    &summary.commits,
                    &summary.sessions,
                    summary.commit_count as i64,
                    summary.session_count as i64,
                    role,
                ).await
            }
        });

        let results = futures::future::join_all(futures).await;

        // Collect successful results
        let insights: Vec<BranchInsight> = results
            .into_iter()
            .filter_map(|r| r.ok())
            .collect();

        if insights.is_empty() {
            Err("All council analyses failed".to_string())
        } else {
            Ok(insights)
        }
    }
}
```

## Quick Reference

| Pattern | Key Rule | Example Location |
|---------|----------|------------------|
| Domain Models | Zero external deps | `components/src/domain.rs` |
| Ports | Trait-based async | `components/src/ports.rs` |
| Adapters | Implement traits | `cli/src/adapters/git.rs` |
| DI | Generic over traits | `cli/src/app.rs` |
| Composition | Unified interface | `cli/src/adapters/unified.rs` |
| Test Doubles | Implement traits | `cli/tests/test_doubles.rs` |
| BAML Integration | Map generated types | `cli/src/adapters/baml.rs` |
| Error Handling | Domain-level errors | All adapters |
| Graceful Degradation | Optional adapters | `cli/src/adapters/unified.rs` |
| Council | Parallel multi-role | `cli/src/adapters/council.rs` |

## Anti-Patterns to Avoid

❌ **Concrete dependencies in App:**
```rust
pub struct App {
    git: GitAdapter, // Couples App to concrete type
}
```

✅ **Generic over traits:**
```rust
pub struct App<B: BranchAggregator> {
    git: Arc<B>, // App is generic, testable
}
```

❌ **External deps in domain:**
```rust
use git2::Oid; // Don't do this!

pub struct Commit {
    oid: Oid, // Couples domain to git2
}
```

✅ **Pure domain types:**
```rust
pub struct Commit {
    hash: String, // Pure std type
}
```

❌ **Leaking infrastructure errors:**
```rust
async fn analyze(&self) -> Result<Insight, git2::Error> {
    // ❌ Exposes git2 error to domain
}
```

✅ **Domain-level errors:**
```rust
async fn analyze(&self) -> Result<Insight, String> {
    // ✅ Generic error for domain layer
}
```

## Conclusion

These patterns enable:
- **Testability** - Easy test doubles without mocking
- **Flexibility** - Swap adapters without changing domain
- **Maintainability** - Clear separation of concerns
- **Resilience** - Graceful degradation when components fail
