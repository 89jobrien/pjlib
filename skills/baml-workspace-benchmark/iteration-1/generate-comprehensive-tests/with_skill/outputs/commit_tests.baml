// Comprehensive test suite for ClassifyCommit function
// Tests cover: basic classifications, edge cases, complex scenarios, and ambiguous commits

// ============================================================================
// BASIC CLASSIFICATIONS - Standard commit types
// ============================================================================

test classify_feature_with_new_files {
  functions [ClassifyCommit]
  args {
    commit_message "feat: add user authentication with OAuth2"
    diff_summary #"
      Added files:
      - src/auth/oauth.rs (OAuth2 implementation)
      - src/auth/jwt.rs (JWT token handling)
      - src/middleware/auth.rs (authentication middleware)
      +245 lines, -0 lines
    "#
  }
}

test classify_bugfix_with_test {
  functions [ClassifyCommit]
  args {
    commit_message "fix: resolve null pointer exception in user profile loading"
    diff_summary #"
      Modified files:
      - src/profile/loader.rs (added null checks)
      - tests/profile/loader_test.rs (added regression test)
      +32 lines, -8 lines
    "#
  }
}

test classify_refactor_extract_method {
  functions [ClassifyCommit]
  args {
    commit_message "refactor: extract duplicated validation logic into shared module"
    diff_summary #"
      Added files:
      - src/validation/common.rs (shared validation utilities)
      Modified files:
      - src/api/users.rs (use common validation)
      - src/api/posts.rs (use common validation)
      - src/api/comments.rs (use common validation)
      +120 lines, -180 lines (net reduction due to deduplication)
    "#
  }
}

test classify_docs_readme_update {
  functions [ClassifyCommit]
  args {
    commit_message "docs: update installation instructions and API examples"
    diff_summary #"
      Modified files:
      - README.md (installation section rewritten)
      - docs/api-guide.md (added code examples)
      +67 lines, -23 lines
    "#
  }
}

test classify_test_coverage_improvement {
  functions [ClassifyCommit]
  args {
    commit_message "test: add integration tests for payment processing"
    diff_summary #"
      Added files:
      - tests/integration/payment_test.rs
      - tests/fixtures/payment_samples.json
      +189 lines, -0 lines
    "#
  }
}

test classify_style_formatting {
  functions [ClassifyCommit]
  args {
    commit_message "style: apply consistent code formatting across codebase"
    diff_summary #"
      Modified files:
      - src/main.rs (formatting only)
      - src/api/handlers.rs (formatting only)
      - src/db/models.rs (formatting only)
      +0 lines, -0 lines (whitespace and formatting changes)
    "#
  }
}

test classify_chore_dependency_update {
  functions [ClassifyCommit]
  args {
    commit_message "chore: update dependencies to latest stable versions"
    diff_summary #"
      Modified files:
      - Cargo.toml (dependency version bumps)
      - Cargo.lock (lock file updated)
      +45 lines, -42 lines
    "#
  }
}

test classify_perf_optimization {
  functions [ClassifyCommit]
  args {
    commit_message "perf: optimize database query performance with connection pooling"
    diff_summary #"
      Modified files:
      - src/db/pool.rs (implement connection pooling)
      - src/config.rs (add pool configuration)
      +78 lines, -15 lines
    "#
  }
}

// ============================================================================
// EDGE CASES - Unusual or boundary conditions
// ============================================================================

test classify_empty_commit_message {
  functions [ClassifyCommit]
  args {
    commit_message ""
    diff_summary #"
      Modified files:
      - src/utils.rs
      +5 lines, -2 lines
    "#
  }
}

test classify_very_long_commit_message {
  functions [ClassifyCommit]
  args {
    commit_message #"
      feat: implement comprehensive multi-tenant architecture with role-based access control, audit logging, data isolation, and tenant-specific configuration management

      This commit introduces a complete multi-tenant system that allows multiple organizations to use the platform while maintaining complete data isolation and security. Each tenant gets their own database schema, custom configuration options, and role-based permissions. The implementation includes middleware for tenant detection, database routing, audit trail logging for compliance, and an admin interface for tenant management. Performance optimizations include connection pooling per tenant and caching of tenant configurations. The change is backward compatible with existing single-tenant deployments.
    "#
    diff_summary #"
      Added files:
      - src/tenant/mod.rs
      - src/tenant/middleware.rs
      - src/tenant/database.rs
      - src/tenant/config.rs
      - src/tenant/rbac.rs
      - src/tenant/audit.rs
      - src/admin/tenant_management.rs
      - migrations/001_multi_tenant_schema.sql
      Modified files:
      - src/main.rs
      - src/config.rs
      - src/db/mod.rs
      +1247 lines, -89 lines
    "#
  }
}

test classify_single_character_change {
  functions [ClassifyCommit]
  args {
    commit_message "fix: typo in configuration key"
    diff_summary #"
      Modified files:
      - src/config.rs
      +1 line, -1 line (changed 'databse' to 'database')
    "#
  }
}

test classify_only_deleted_files {
  functions [ClassifyCommit]
  args {
    commit_message "chore: remove deprecated authentication module"
    diff_summary #"
      Deleted files:
      - src/auth/legacy.rs
      - src/auth/deprecated_oauth.rs
      - tests/auth/legacy_test.rs
      +0 lines, -456 lines
    "#
  }
}

test classify_ambiguous_short_message {
  functions [ClassifyCommit]
  args {
    commit_message "update stuff"
    diff_summary #"
      Modified files:
      - src/api/handlers.rs
      - src/models/user.rs
      +23 lines, -18 lines
    "#
  }
}

// ============================================================================
// COMPLEX SCENARIOS - Real-world complex commits
// ============================================================================

test classify_mixed_feature_and_bugfix {
  functions [ClassifyCommit]
  args {
    commit_message "feat: add email notifications and fix race condition in message queue"
    diff_summary #"
      Added files:
      - src/notifications/email.rs (new feature)
      - src/notifications/templates/ (email templates)
      Modified files:
      - src/queue/processor.rs (fixed race condition with mutex)
      - src/models/notification.rs
      +234 lines, -12 lines
    "#
  }
}

test classify_breaking_change {
  functions [ClassifyCommit]
  args {
    commit_message #"
      feat!: migrate API from v1 to v2 with breaking changes

      BREAKING CHANGE: The authentication endpoint has been moved from /auth to /v2/authenticate and now requires a different token format
    "#
    diff_summary #"
      Added files:
      - src/api/v2/auth.rs
      - src/api/v2/handlers.rs
      Modified files:
      - src/api/router.rs (route changes)
      - src/api/v1/auth.rs (marked as deprecated)
      - docs/migration-guide.md
      +456 lines, -78 lines
    "#
  }
}

test classify_revert_commit {
  functions [ClassifyCommit]
  args {
    commit_message "revert: revert 'feat: add experimental caching layer'"
    diff_summary #"
      Deleted files:
      - src/cache/experimental.rs
      Modified files:
      - src/main.rs (removed cache initialization)
      - Cargo.toml (removed cache dependencies)
      +0 lines, -234 lines
    "#
  }
}

test classify_merge_commit {
  functions [ClassifyCommit]
  args {
    commit_message "Merge pull request #42 from feature/user-dashboard"
    diff_summary #"
      Added files:
      - src/dashboard/mod.rs
      - src/dashboard/widgets.rs
      - templates/dashboard.html
      Modified files:
      - src/routes.rs
      +389 lines, -15 lines
    "#
  }
}

test classify_security_fix {
  functions [ClassifyCommit]
  args {
    commit_message "security: fix SQL injection vulnerability in search endpoint"
    diff_summary #"
      Modified files:
      - src/api/search.rs (replaced string concat with parameterized queries)
      - tests/security/sql_injection_test.rs (added security tests)
      +67 lines, -23 lines
    "#
  }
}

test classify_wip_commit {
  functions [ClassifyCommit]
  args {
    commit_message "WIP: working on new analytics dashboard"
    diff_summary #"
      Added files:
      - src/analytics/dashboard.rs (incomplete)
      Modified files:
      - src/analytics/mod.rs
      +156 lines, -0 lines
    "#
  }
}

test classify_hotfix_production {
  functions [ClassifyCommit]
  args {
    commit_message "hotfix: critical memory leak in connection pool"
    diff_summary #"
      Modified files:
      - src/db/pool.rs (fixed connection cleanup logic)
      +8 lines, -3 lines
    "#
  }
}

// ============================================================================
// AMBIGUOUS CASES - Difficult to classify
// ============================================================================

test classify_rename_only {
  functions [ClassifyCommit]
  args {
    commit_message "rename handlers to controllers for consistency"
    diff_summary #"
      Renamed files:
      - src/api/handlers.rs -> src/api/controllers.rs
      - src/api/handlers/ -> src/api/controllers/
      +0 lines, -0 lines (pure rename, no content changes)
    "#
  }
}

test classify_config_changes_only {
  functions [ClassifyCommit]
  args {
    commit_message "update production configuration"
    diff_summary #"
      Modified files:
      - config/production.toml (changed timeout values)
      - .env.example (added new environment variables)
      +12 lines, -8 lines
    "#
  }
}

test classify_whitespace_only {
  functions [ClassifyCommit]
  args {
    commit_message "clean up trailing whitespace"
    diff_summary #"
      Modified files:
      - src/main.rs (removed trailing whitespace)
      - src/api/mod.rs (removed trailing whitespace)
      - src/db/mod.rs (removed trailing whitespace)
      +0 lines, -0 lines (whitespace only)
    "#
  }
}

test classify_initial_commit {
  functions [ClassifyCommit]
  args {
    commit_message "initial commit"
    diff_summary #"
      Added files:
      - src/main.rs
      - Cargo.toml
      - README.md
      - .gitignore
      +234 lines, -0 lines
    "#
  }
}

// ============================================================================
// CONVENTIONAL COMMITS FORMAT - Various prefix styles
// ============================================================================

test classify_conventional_feat_scope {
  functions [ClassifyCommit]
  args {
    commit_message "feat(auth): add two-factor authentication support"
    diff_summary #"
      Added files:
      - src/auth/totp.rs
      - src/auth/backup_codes.rs
      Modified files:
      - src/auth/mod.rs
      +178 lines, -12 lines
    "#
  }
}

test classify_conventional_fix_scope {
  functions [ClassifyCommit]
  args {
    commit_message "fix(api): handle timeout errors gracefully"
    diff_summary #"
      Modified files:
      - src/api/client.rs (added timeout error handling)
      +45 lines, -8 lines
    "#
  }
}

test classify_build_system_changes {
  functions [ClassifyCommit]
  args {
    commit_message "build: migrate from Webpack to Vite"
    diff_summary #"
      Added files:
      - vite.config.js
      Deleted files:
      - webpack.config.js
      Modified files:
      - package.json
      +89 lines, -145 lines
    "#
  }
}

test classify_ci_pipeline_update {
  functions [ClassifyCommit]
  args {
    commit_message "ci: add automated security scanning to pipeline"
    diff_summary #"
      Added files:
      - .github/workflows/security-scan.yml
      Modified files:
      - .github/workflows/ci.yml
      +67 lines, -5 lines
    "#
  }
}
