// Comprehensive Test Suite for ClassifyCommit Function
// Coverage includes: features, bugfixes, refactors, docs, tests, chores, and edge cases

// ========================================
// FEATURE TESTS
// ========================================

test ClassifyFeature_AddNewEndpoint {
  functions [ClassifyCommit]
  args {
    commit_message "feat: add user authentication endpoint"
    diff_summary "Added POST /api/auth/login endpoint with JWT support, added middleware for token validation, created auth service"
  }
}

test ClassifyFeature_NewComponent {
  functions [ClassifyCommit]
  args {
    commit_message "Add user profile component"
    diff_summary "Created UserProfile.tsx component with avatar display, bio section, and edit functionality. Added styling and unit tests."
  }
}

test ClassifyFeature_DatabaseMigration {
  functions [ClassifyCommit]
  args {
    commit_message "feat(db): add user_preferences table"
    diff_summary "Added migration 2024_03_10_create_user_preferences.sql with columns: id, user_id, theme, language, notifications. Added foreign key to users table."
  }
}

test ClassifyFeature_ComplexNewFeature {
  functions [ClassifyCommit]
  args {
    commit_message "Implement real-time notifications system"
    diff_summary "Added WebSocket server setup, notification queue using Redis, frontend notification component, notification persistence layer, push notification integration"
  }
}

test ClassifyFeature_ConventionalCommit {
  functions [ClassifyCommit]
  args {
    commit_message "feat(api)!: introduce GraphQL API alongside REST"
    diff_summary "Added Apollo Server, GraphQL schema definitions, resolvers for users/posts/comments, graphql playground endpoint at /graphql"
  }
}

// ========================================
// BUGFIX TESTS
// ========================================

test ClassifyBugfix_NullPointer {
  functions [ClassifyCommit]
  args {
    commit_message "fix: prevent null pointer exception in user service"
    diff_summary "Added null check before accessing user.profile.email, added defensive validation in getUserById method"
  }
}

test ClassifyBugfix_RaceCondition {
  functions [ClassifyCommit]
  args {
    commit_message "Fix race condition in payment processing"
    diff_summary "Added mutex lock around transaction creation, ensured atomic update of payment status, added transaction isolation level"
  }
}

test ClassifyBugfix_MemoryLeak {
  functions [ClassifyCommit]
  args {
    commit_message "fix(frontend): resolve memory leak in dashboard"
    diff_summary "Added cleanup in useEffect hooks, removed event listeners on component unmount, cancelled pending API requests in cleanup"
  }
}

test ClassifyBugfix_SecurityVulnerability {
  functions [ClassifyCommit]
  args {
    commit_message "fix: patch SQL injection vulnerability in search"
    diff_summary "Replaced string concatenation with parameterized queries, added input sanitization, updated all raw SQL calls to use prepared statements"
  }
}

test ClassifyBugfix_CriticalProduction {
  functions [ClassifyCommit]
  args {
    commit_message "HOTFIX: restore database connection pool"
    diff_summary "Increased connection pool max size from 10 to 50, added connection retry logic with exponential backoff, fixed connection leak in error handler"
  }
}

test ClassifyBugfix_CrashOnEdgeCase {
  functions [ClassifyCommit]
  args {
    commit_message "fix: handle empty array in data processor"
    diff_summary "Added early return when input array is empty, prevent division by zero, added validation for minimum required data points"
  }
}

// ========================================
// REFACTOR TESTS
// ========================================

test ClassifyRefactor_CodeCleanup {
  functions [ClassifyCommit]
  args {
    commit_message "refactor: simplify user authentication logic"
    diff_summary "Extracted password hashing to utility function, removed duplicate validation code, consolidated error handling patterns"
  }
}

test ClassifyRefactor_ArchitectureChange {
  functions [ClassifyCommit]
  args {
    commit_message "refactor(core): migrate to hexagonal architecture"
    diff_summary "Separated domain logic from infrastructure, created ports and adapters, moved business rules to domain layer, updated dependency injection"
  }
}

test ClassifyRefactor_ExtractModule {
  functions [ClassifyCommit]
  args {
    commit_message "Extract email service into separate module"
    diff_summary "Created email-service package, moved all email-related code from main app, defined email service interface, updated imports across 15 files"
  }
}

test ClassifyRefactor_TypeScriptMigration {
  functions [ClassifyCommit]
  args {
    commit_message "refactor: convert utils from JavaScript to TypeScript"
    diff_summary "Renamed .js files to .ts, added type annotations, defined interfaces for function parameters, fixed type errors, updated tsconfig"
  }
}

test ClassifyRefactor_PerformanceOptimization {
  functions [ClassifyCommit]
  args {
    commit_message "refactor: optimize database queries with eager loading"
    diff_summary "Replaced N+1 queries with joins, added select optimization to fetch only needed columns, implemented query result caching"
  }
}

test ClassifyRefactor_RenameVariables {
  functions [ClassifyCommit]
  args {
    commit_message "Rename ambiguous variable names for clarity"
    diff_summary "Renamed 'data' to 'userData', 'temp' to 'processedResults', 'x' to 'userId' across 8 files, updated related comments"
  }
}

// ========================================
// DOCUMENTATION TESTS
// ========================================

test ClassifyDocs_APIDocumentation {
  functions [ClassifyCommit]
  args {
    commit_message "docs: add API documentation for authentication endpoints"
    diff_summary "Updated README.md with authentication flow, added OpenAPI/Swagger specs, documented request/response examples"
  }
}

test ClassifyDocs_CodeComments {
  functions [ClassifyCommit]
  args {
    commit_message "docs: add JSDoc comments to utility functions"
    diff_summary "Added JSDoc comments to all 23 utility functions, documented parameters and return types, added usage examples in comments"
  }
}

test ClassifyDocs_ReadmeUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "Update README with installation instructions"
    diff_summary "Added prerequisites section, updated npm install commands, added troubleshooting section, fixed broken links"
  }
}

test ClassifyDocs_ArchitectureDiagram {
  functions [ClassifyCommit]
  args {
    commit_message "docs(architecture): add system design diagrams"
    diff_summary "Added docs/architecture.md with Mermaid diagrams, documented data flow, added component interaction diagrams"
  }
}

test ClassifyDocs_ChangelogUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "docs: update CHANGELOG for v2.5.0 release"
    diff_summary "Added release notes for version 2.5.0, documented breaking changes, listed new features and bug fixes"
  }
}

// ========================================
// TEST-RELATED COMMITS
// ========================================

test ClassifyTest_AddUnitTests {
  functions [ClassifyCommit]
  args {
    commit_message "test: add unit tests for payment service"
    diff_summary "Created payment.service.test.ts with 15 test cases, tested success scenarios, error handling, edge cases, achieved 95% coverage"
  }
}

test ClassifyTest_AddIntegrationTests {
  functions [ClassifyCommit]
  args {
    commit_message "test(api): add integration tests for user endpoints"
    diff_summary "Added integration tests for GET/POST/PUT/DELETE /api/users, tested authentication, authorization, validation errors"
  }
}

test ClassifyTest_FixFlakyTests {
  functions [ClassifyCommit]
  args {
    commit_message "test: fix flaky timing-dependent tests"
    diff_summary "Replaced setTimeout with waitFor, added proper async/await, increased timeouts for CI environment, mocked Date.now()"
  }
}

test ClassifyTest_UpdateTestSnapshots {
  functions [ClassifyCommit]
  args {
    commit_message "test: update component snapshots"
    diff_summary "Updated Jest snapshots for UserProfile, Dashboard, Navigation components after UI changes"
  }
}

test ClassifyTest_AddE2ETests {
  functions [ClassifyCommit]
  args {
    commit_message "test(e2e): add Playwright tests for checkout flow"
    diff_summary "Added end-to-end tests for complete checkout process, tested cart management, payment processing, order confirmation"
  }
}

// ========================================
// CHORE/MAINTENANCE TESTS
// ========================================

test ClassifyChore_DependencyUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "chore: update dependencies to latest versions"
    diff_summary "Updated package.json: react 18.2.0 -> 18.3.0, next 14.0.0 -> 14.1.0, updated lock file, ran tests"
  }
}

test ClassifyChore_ConfigurationChange {
  functions [ClassifyCommit]
  args {
    commit_message "chore(config): update ESLint configuration"
    diff_summary "Updated .eslintrc.json with stricter rules, added TypeScript-specific rules, disabled console warnings in tests"
  }
}

test ClassifyChore_BuildOptimization {
  functions [ClassifyCommit]
  args {
    commit_message "chore: optimize webpack build configuration"
    diff_summary "Added code splitting configuration, enabled tree shaking, configured chunk optimization, reduced bundle size by 30%"
  }
}

test ClassifyChore_CIUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "chore(ci): update GitHub Actions workflow"
    diff_summary "Updated .github/workflows/ci.yml to use Node 20, added caching for dependencies, parallelized test execution"
  }
}

test ClassifyChore_Formatting {
  functions [ClassifyCommit]
  args {
    commit_message "chore: run prettier on all files"
    diff_summary "Formatted 127 files with Prettier, standardized quote style, fixed indentation, updated .prettierrc"
  }
}

// ========================================
// STYLE/COSMETIC TESTS
// ========================================

test ClassifyStyle_CSSUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "style: improve button hover animations"
    diff_summary "Updated button.css with smoother transitions, added subtle shadow on hover, adjusted color contrast for accessibility"
  }
}

test ClassifyStyle_LayoutAdjustment {
  functions [ClassifyCommit]
  args {
    commit_message "style(ui): adjust spacing and alignment in header"
    diff_summary "Updated header component margins, aligned logo and navigation, improved responsive breakpoints, fixed mobile menu overlap"
  }
}

test ClassifyStyle_LintFixes {
  functions [ClassifyCommit]
  args {
    commit_message "style: fix linting errors and warnings"
    diff_summary "Fixed unused imports, removed trailing whitespace, fixed indentation, sorted imports alphabetically, no functional changes"
  }
}

// ========================================
// PERFORMANCE TESTS
// ========================================

test ClassifyPerformance_CachingImplementation {
  functions [ClassifyCommit]
  args {
    commit_message "perf: add Redis caching for user queries"
    diff_summary "Implemented Redis caching layer, added cache invalidation on updates, set TTL to 5 minutes, reduced DB load by 70%"
  }
}

test ClassifyPerformance_LazyLoading {
  functions [ClassifyCommit]
  args {
    commit_message "perf(frontend): implement lazy loading for routes"
    diff_summary "Added React.lazy() for all route components, implemented Suspense boundaries, reduced initial bundle size from 2MB to 500KB"
  }
}

test ClassifyPerformance_DatabaseIndexing {
  functions [ClassifyCommit]
  args {
    commit_message "perf(db): add indexes for frequently queried columns"
    diff_summary "Added indexes on users.email, orders.created_at, products.category_id, reduced query time from 2s to 50ms"
  }
}

// ========================================
// BUILD/DEPLOYMENT TESTS
// ========================================

test ClassifyBuild_DockerConfiguration {
  functions [ClassifyCommit]
  args {
    commit_message "build: optimize Dockerfile for faster builds"
    diff_summary "Updated Dockerfile with multi-stage build, added layer caching for dependencies, reduced image size from 1.2GB to 400MB"
  }
}

test ClassifyBuild_ReleasePreparation {
  functions [ClassifyCommit]
  args {
    commit_message "build: prepare for v3.0.0 release"
    diff_summary "Updated version in package.json, generated changelog, tagged release, built production artifacts"
  }
}

// ========================================
// REVERT TESTS
// ========================================

test ClassifyRevert_RollbackFeature {
  functions [ClassifyCommit]
  args {
    commit_message "revert: rollback experimental caching feature"
    diff_summary "Reverted commit abc123, removed caching layer causing production issues, restored previous implementation"
  }
}

test ClassifyRevert_UndoBreakingChange {
  functions [ClassifyCommit]
  args {
    commit_message "Revert \"Update API response format\""
    diff_summary "This reverts commit def456. Breaking change caused client errors, restoring original response structure"
  }
}

// ========================================
// EDGE CASES & AMBIGUOUS COMMITS
// ========================================

test ClassifyEdgeCase_VagueMessage {
  functions [ClassifyCommit]
  args {
    commit_message "Update files"
    diff_summary "Modified user.service.ts, updated README.md, changed config.json, reformatted components/Button.tsx"
  }
}

test ClassifyEdgeCase_EmptyDiff {
  functions [ClassifyCommit]
  args {
    commit_message "fix: resolve production issue"
    diff_summary ""
  }
}

test ClassifyEdgeCase_MassiveRefactor {
  functions [ClassifyCommit]
  args {
    commit_message "Major overhaul of application architecture"
    diff_summary "Migrated from REST to GraphQL, converted all components to TypeScript, restructured folder layout, updated all dependencies, rewrote authentication system, added comprehensive test coverage. Changed 243 files."
  }
}

test ClassifyEdgeCase_WIPCommit {
  functions [ClassifyCommit]
  args {
    commit_message "WIP: working on new feature"
    diff_summary "Partial implementation of notification system, incomplete tests, commented out code, temporary debugging statements"
  }
}

test ClassifyEdgeCase_MergeCommit {
  functions [ClassifyCommit]
  args {
    commit_message "Merge branch 'feature/user-profiles' into main"
    diff_summary "Merged 23 commits from feature branch including: user profile UI, profile editing, avatar upload, privacy settings"
  }
}

test ClassifyEdgeCase_TypoFix {
  functions [ClassifyCommit]
  args {
    commit_message "Fix typo in variable name"
    diff_summary "Renamed 'usre' to 'user' in auth.service.ts line 42"
  }
}

test ClassifyEdgeCase_InitialCommit {
  functions [ClassifyCommit]
  args {
    commit_message "Initial commit"
    diff_summary "Added project scaffolding, package.json, basic folder structure, README, .gitignore, initial configuration files"
  }
}

test ClassifyEdgeCase_MultipleTypes {
  functions [ClassifyCommit]
  args {
    commit_message "Add new feature and fix existing bugs"
    diff_summary "Added CSV export functionality (new feature), fixed memory leak in data processor, refactored export service, updated tests"
  }
}

test ClassifyEdgeCase_SecurityUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "Security update: patch authentication vulnerability"
    diff_summary "Updated JWT library to patch CVE-2024-1234, regenerated all tokens, added additional validation, updated security documentation"
  }
}

test ClassifyEdgeCase_OnlyComments {
  functions [ClassifyCommit]
  args {
    commit_message "Add comments explaining complex algorithm"
    diff_summary "Added detailed comments to sorting algorithm explaining time/space complexity, documented edge cases, no code changes"
  }
}

test ClassifyEdgeCase_LicenseUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "Update license to MIT"
    diff_summary "Changed LICENSE file from Apache 2.0 to MIT, updated copyright headers in all source files"
  }
}

test ClassifyEdgeCase_DotfilesUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "Update .gitignore and .env.example"
    diff_summary "Added node_modules, .DS_Store, build/ to .gitignore, added new environment variables to .env.example"
  }
}

// ========================================
// REAL-WORLD SCENARIO TESTS
// ========================================

test ClassifyRealWorld_ConventionalCommitFeature {
  functions [ClassifyCommit]
  args {
    commit_message "feat(auth): implement OAuth2 social login"
    diff_summary "Added OAuth2 client configuration, implemented Google/GitHub login flows, created callback handlers, added user linking logic, updated UI with social login buttons"
  }
}

test ClassifyRealWorld_ConventionalCommitFix {
  functions [ClassifyCommit]
  args {
    commit_message "fix(api): correct pagination offset calculation"
    diff_summary "Fixed off-by-one error in pagination logic, corrected offset calculation when page size changes, added tests for edge cases"
  }
}

test ClassifyRealWorld_BranchingWorkflow {
  functions [ClassifyCommit]
  args {
    commit_message "Merge pull request #456 from feature/shopping-cart"
    diff_summary "Merged shopping cart feature: add to cart, remove items, update quantities, persist cart, checkout integration. Includes 8 commits and 2500 lines changed."
  }
}

test ClassifyRealWorld_DependencyVulnerabilityFix {
  functions [ClassifyCommit]
  args {
    commit_message "chore(deps): bump lodash to fix security vulnerability"
    diff_summary "Updated lodash from 4.17.20 to 4.17.21 to address prototype pollution vulnerability (CVE-2021-23337), ran npm audit fix"
  }
}

test ClassifyRealWorld_BackwardCompatibility {
  functions [ClassifyCommit]
  args {
    commit_message "feat: add new API v2 while maintaining v1 compatibility"
    diff_summary "Created /api/v2 endpoints with improved response format, kept /api/v1 unchanged, added version negotiation middleware, updated documentation"
  }
}

test ClassifyRealWorld_DatabaseMigrationRollback {
  functions [ClassifyCommit]
  args {
    commit_message "fix(db): add rollback migration for failed user_settings table"
    diff_summary "Created down migration to revert user_settings table changes, restored previous schema, added migration safety checks"
  }
}

test ClassifyRealWorld_MonorepoUpdate {
  functions [ClassifyCommit]
  args {
    commit_message "chore: update all packages in monorepo"
    diff_summary "Updated dependencies across 12 packages, synchronized version numbers, updated workspace configurations, fixed breaking changes"
  }
}

test ClassifyRealWorld_AccessibilityImprovement {
  functions [ClassifyCommit]
  args {
    commit_message "feat(a11y): improve keyboard navigation and screen reader support"
    diff_summary "Added ARIA labels, implemented focus management, added keyboard shortcuts, improved color contrast, tested with NVDA/JAWS"
  }
}

test ClassifyRealWorld_InternationalizationSetup {
  functions [ClassifyCommit]
  args {
    commit_message "feat(i18n): add internationalization support"
    diff_summary "Integrated react-i18next, extracted all UI strings to translation files, added English and Spanish translations, implemented language switcher"
  }
}

test ClassifyRealWorld_CIFailureFix {
  functions [ClassifyCommit]
  args {
    commit_message "fix(ci): resolve failing tests in CI environment"
    diff_summary "Fixed timezone-dependent tests, adjusted timeouts for slower CI runners, updated test database seeding, mocked external API calls"
  }
}
