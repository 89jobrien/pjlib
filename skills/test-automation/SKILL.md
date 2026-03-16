---
name: test-automation
description: Comprehensive test automation patterns including test suite architecture, unit/integration/E2E testing frameworks, performance testing, CI/CD integration, and quality metrics. Use when implementing test strategies, setting up test automation, configuring test frameworks, or establishing quality gates.
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
---

# Test Automation

You are an expert in test automation, specializing in comprehensive testing strategies from unit tests to E2E testing, with focus on automation, quality metrics, and CI/CD integration.

## When to Use This Skill

Use this skill whenever:
- Setting up test automation infrastructure
- Implementing test frameworks (Jest, Playwright, pytest)
- Creating test suite architectures
- Establishing quality gates and coverage thresholds
- Configuring CI/CD test pipelines
- Performance and load testing
- The user mentions test automation, testing strategy, or quality assurance

## Testing Strategy Framework

### Test Pyramid

**Unit Tests (70%)**
- Fast, isolated tests
- Mock dependencies
- High coverage of business logic
- Run in milliseconds

**Integration Tests (20%)**
- Test component interactions
- Real database/service connections
- API contract testing
- Run in seconds

**E2E Tests (10%)**
- Full user journey testing
- Browser automation
- Critical path validation
- Run in minutes

### Testing Types

**Functional Testing**
- Feature validation
- Business logic verification
- User acceptance testing (UAT)

**Non-Functional Testing**
- Performance testing (load, stress, spike)
- Security testing
- Accessibility testing
- Compatibility testing

**Regression Testing**
- Automated after each change
- Prevent bug reintroduction
- Smoke tests for critical paths

## Technical Implementation

### 1. Comprehensive Test Suite Architecture

**Test Suite Manager (JavaScript)**

```javascript
// test-framework/test-suite-manager.js
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

class TestSuiteManager {
  constructor(config = {}) {
    this.config = {
      testDirectory: "./tests",
      coverageThreshold: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
      testPatterns: {
        unit: "**/*.test.js",
        integration: "**/*.integration.test.js",
        e2e: "**/*.e2e.test.js",
      },
      ...config,
    };

    this.testResults = {
      unit: null,
      integration: null,
      e2e: null,
      coverage: null,
    };
  }

  async runFullTestSuite() {
    console.log("Starting comprehensive test suite...");

    try {
      await this.runUnitTests();
      await this.runIntegrationTests();
      await this.runE2ETests();
      await this.generateCoverageReport();

      const summary = this.generateTestSummary();
      await this.publishTestResults(summary);

      return summary;
    } catch (error) {
      console.error("Test suite failed:", error.message);
      throw error;
    }
  }

  async runUnitTests() {
    console.log("Running unit tests...");

    const jestConfig = {
      testMatch: [this.config.testPatterns.unit],
      collectCoverage: true,
      collectCoverageFrom: [
        "src/**/*.{js,ts}",
        "!src/**/*.test.{js,ts}",
        "!src/**/*.spec.{js,ts}",
        "!src/test/**/*",
      ],
      coverageReporters: ["text", "lcov", "html", "json"],
      coverageThreshold: this.config.coverageThreshold,
      testEnvironment: "jsdom",
      setupFilesAfterEnv: ["<rootDir>/src/test/setup.js"],
      moduleNameMapping: {
        "^@/(.*)$": "<rootDir>/src/$1",
      },
    };

    try {
      const command = `npx jest --config='${JSON.stringify(jestConfig)}' --passWithNoTests`;
      const result = execSync(command, { encoding: "utf8", stdio: "pipe" });

      this.testResults.unit = {
        status: "passed",
        output: result,
        timestamp: new Date().toISOString(),
      };

      console.log("Unit tests passed");
    } catch (error) {
      this.testResults.unit = {
        status: "failed",
        output: error.stdout || error.message,
        error: error.stderr || error.message,
        timestamp: new Date().toISOString(),
      };

      throw new Error(`Unit tests failed: ${error.message}`);
    }
  }

  async runIntegrationTests() {
    console.log("Running integration tests...");

    await this.setupTestEnvironment();

    try {
      const command = `npx jest --testMatch="${this.config.testPatterns.integration}" --runInBand`;
      const result = execSync(command, { encoding: "utf8", stdio: "pipe" });

      this.testResults.integration = {
        status: "passed",
        output: result,
        timestamp: new Date().toISOString(),
      };

      console.log("Integration tests passed");
    } catch (error) {
      this.testResults.integration = {
        status: "failed",
        output: error.stdout || error.message,
        error: error.stderr || error.message,
        timestamp: new Date().toISOString(),
      };

      throw new Error(`Integration tests failed: ${error.message}`);
    } finally {
      await this.teardownTestEnvironment();
    }
  }

  async runE2ETests() {
    console.log("Running E2E tests...");

    try {
      const command = `npx playwright test --config=playwright.config.js`;
      const result = execSync(command, { encoding: "utf8", stdio: "pipe" });

      this.testResults.e2e = {
        status: "passed",
        output: result,
        timestamp: new Date().toISOString(),
      };

      console.log("E2E tests passed");
    } catch (error) {
      this.testResults.e2e = {
        status: "failed",
        output: error.stdout || error.message,
        error: error.stderr || error.message,
        timestamp: new Date().toISOString(),
      };

      throw new Error(`E2E tests failed: ${error.message}`);
    }
  }

  async setupTestEnvironment() {
    console.log("Setting up test environment...");

    try {
      execSync(
        "docker-compose -f docker-compose.test.yml up -d postgres redis",
        { stdio: "pipe" },
      );

      await this.waitForServices();
      execSync("npm run db:migrate:test", { stdio: "pipe" });
      execSync("npm run db:seed:test", { stdio: "pipe" });
    } catch (error) {
      throw new Error(`Failed to setup test environment: ${error.message}`);
    }
  }

  async teardownTestEnvironment() {
    console.log("Cleaning up test environment...");

    try {
      execSync("docker-compose -f docker-compose.test.yml down", {
        stdio: "pipe",
      });
    } catch (error) {
      console.warn(
        "Warning: Failed to cleanup test environment:",
        error.message,
      );
    }
  }

  async waitForServices(timeout = 30000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      try {
        execSync("pg_isready -h localhost -p 5433", { stdio: "pipe" });
        execSync("redis-cli -p 6380 ping", { stdio: "pipe" });
        return;
      } catch (error) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }

    throw new Error("Test services failed to start within timeout");
  }

  generateTestSummary() {
    const summary = {
      timestamp: new Date().toISOString(),
      overall: {
        status: this.determineOverallStatus(),
        duration: this.calculateTotalDuration(),
        testsRun: this.countTotalTests(),
      },
      results: this.testResults,
      coverage: this.parseCoverageReport(),
      recommendations: this.generateRecommendations(),
    };

    console.log("\nTest Summary:");
    console.log(`Overall Status: ${summary.overall.status}`);
    console.log(`Total Duration: ${summary.overall.duration}ms`);
    console.log(`Tests Run: ${summary.overall.testsRun}`);

    return summary;
  }

  determineOverallStatus() {
    const results = Object.values(this.testResults);
    const failures = results.filter(
      (result) => result && result.status === "failed",
    );
    return failures.length === 0 ? "PASSED" : "FAILED";
  }

  generateRecommendations() {
    const recommendations = [];

    const coverage = this.parseCoverageReport();
    if (coverage && coverage.total.lines.pct < 80) {
      recommendations.push({
        category: "coverage",
        severity: "medium",
        issue: "Low test coverage",
        recommendation: `Increase line coverage from ${coverage.total.lines.pct}% to at least 80%`,
      });
    }

    Object.entries(this.testResults).forEach(([type, result]) => {
      if (result && result.status === "failed") {
        recommendations.push({
          category: "test-failure",
          severity: "high",
          issue: `${type} tests failing`,
          recommendation: `Review and fix failing ${type} tests before deployment`,
        });
      }
    });

    return recommendations;
  }

  parseCoverageReport() {
    try {
      const coveragePath = path.join(
        process.cwd(),
        "coverage/coverage-summary.json",
      );
      if (fs.existsSync(coveragePath)) {
        return JSON.parse(fs.readFileSync(coveragePath, "utf8"));
      }
    } catch (error) {
      console.warn("Could not parse coverage report:", error.message);
    }
    return null;
  }
}

module.exports = { TestSuiteManager };
```

### 2. Advanced Test Patterns

**Page Object Model & Test Helpers**

```javascript
// test-framework/test-patterns.js

class TestPatterns {
  // Page Object Model for E2E tests
  static createPageObject(page, selectors) {
    const pageObject = {};

    Object.entries(selectors).forEach(([name, selector]) => {
      pageObject[name] = {
        element: () => page.locator(selector),
        click: () => page.click(selector),
        fill: (text) => page.fill(selector, text),
        getText: () => page.textContent(selector),
        isVisible: () => page.isVisible(selector),
        waitFor: (options) => page.waitForSelector(selector, options),
      };
    });

    return pageObject;
  }

  // Test data factory
  static createTestDataFactory(schema) {
    return {
      build: (overrides = {}) => {
        const data = {};

        Object.entries(schema).forEach(([key, generator]) => {
          if (overrides[key] !== undefined) {
            data[key] = overrides[key];
          } else if (typeof generator === "function") {
            data[key] = generator();
          } else {
            data[key] = generator;
          }
        });

        return data;
      },

      buildList: (count, overrides = {}) => {
        return Array.from({ length: count }, (_, index) =>
          this.build({ ...overrides, id: index + 1 }),
        );
      },
    };
  }

  // Mock service factory
  static createMockService(serviceName, methods) {
    const mock = {};

    methods.forEach((method) => {
      mock[method] = jest.fn();
    });

    mock.reset = () => {
      methods.forEach((method) => {
        mock[method].mockReset();
      });
    };

    mock.restore = () => {
      methods.forEach((method) => {
        mock[method].mockRestore();
      });
    };

    return mock;
  }

  // Database test helpers
  static createDatabaseTestHelpers(db) {
    return {
      async cleanTables(tableNames) {
        for (const tableName of tableNames) {
          await db.query(
            `TRUNCATE TABLE ${tableName} RESTART IDENTITY CASCADE`,
          );
        }
      },

      async seedTable(tableName, data) {
        if (Array.isArray(data)) {
          for (const row of data) {
            await db.query(
              `INSERT INTO ${tableName} (${Object.keys(row).join(", ")}) VALUES (${Object.keys(
                row,
              )
                .map((_, i) => `$${i + 1}`)
                .join(", ")})`,
              Object.values(row),
            );
          }
        } else {
          await db.query(
            `INSERT INTO ${tableName} (${Object.keys(data).join(", ")}) VALUES (${Object.keys(
              data,
            )
              .map((_, i) => `$${i + 1}`)
              .join(", ")})`,
            Object.values(data),
          );
        }
      },

      async getLastInserted(tableName) {
        const result = await db.query(
          `SELECT * FROM ${tableName} ORDER BY id DESC LIMIT 1`,
        );
        return result.rows[0];
      },
    };
  }

  // API test helpers
  static createAPITestHelpers(baseURL) {
    const axios = require("axios");

    const client = axios.create({
      baseURL,
      timeout: 10000,
      validateStatus: () => true,
    });

    return {
      async get(endpoint, options = {}) {
        return await client.get(endpoint, options);
      },

      async post(endpoint, data, options = {}) {
        return await client.post(endpoint, data, options);
      },

      async put(endpoint, data, options = {}) {
        return await client.put(endpoint, data, options);
      },

      async delete(endpoint, options = {}) {
        return await client.delete(endpoint, options);
      },

      withAuth(token) {
        client.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        return this;
      },

      clearAuth() {
        delete client.defaults.headers.common["Authorization"];
        return this;
      },
    };
  }
}

module.exports = { TestPatterns };
```

### 3. Test Configuration Templates

**Playwright E2E Configuration**

```javascript
// playwright.config.js
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html"],
    ["json", { outputFile: "test-results/e2e-results.json" }],
    ["junit", { outputFile: "test-results/e2e-results.xml" }],
  ],
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
    {
      name: "Mobile Safari",
      use: { ...devices["iPhone 12"] },
    },
  ],
  webServer: {
    command: "npm run start:test",
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

**Jest Unit/Integration Configuration**

```javascript
// jest.config.js
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  roots: ["<rootDir>/src"],
  testMatch: [
    "**/__tests__/**/*.+(ts|tsx|js)",
    "**/*.(test|spec).+(ts|tsx|js)",
  ],
  transform: {
    "^.+\\.(ts|tsx)$": "ts-jest",
  },
  collectCoverageFrom: [
    "src/**/*.{js,jsx,ts,tsx}",
    "!src/**/*.d.ts",
    "!src/test/**/*",
    "!src/**/*.stories.*",
    "!src/**/*.test.*",
  ],
  coverageReporters: ["text", "lcov", "html", "json-summary"],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ["<rootDir>/src/test/setup.ts"],
  moduleNameMapping: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
  },
  testTimeout: 10000,
  maxWorkers: "50%",
};
```

### 4. Performance Testing Framework

Save as `scripts/performance_testing.js`:

```javascript
// Performance testing implementation
const { performance } = require("perf_hooks");

class PerformanceTestFramework {
  constructor() {
    this.benchmarks = new Map();
    this.thresholds = {
      responseTime: 1000,
      throughput: 100,
      errorRate: 0.01,
    };
  }

  async runLoadTest(config) {
    const {
      endpoint,
      method = "GET",
      payload,
      concurrent = 10,
      duration = 60000,
      rampUp = 5000,
    } = config;

    console.log(`Starting load test: ${concurrent} users for ${duration}ms`);

    const results = {
      requests: [],
      errors: [],
      startTime: Date.now(),
      endTime: null,
    };

    const userPromises = [];
    for (let i = 0; i < concurrent; i++) {
      const delay = (rampUp / concurrent) * i;
      userPromises.push(
        this.simulateUser(
          endpoint,
          method,
          payload,
          duration - delay,
          delay,
          results,
        ),
      );
    }

    await Promise.all(userPromises);
    results.endTime = Date.now();

    return this.analyzeResults(results);
  }

  async simulateUser(endpoint, method, payload, duration, delay, results) {
    await new Promise((resolve) => setTimeout(resolve, delay));

    const endTime = Date.now() + duration;

    while (Date.now() < endTime) {
      const startTime = performance.now();

      try {
        const response = await this.makeRequest(endpoint, method, payload);
        const endTime = performance.now();

        results.requests.push({
          startTime,
          endTime,
          duration: endTime - startTime,
          status: response.status,
          size: response.data ? JSON.stringify(response.data).length : 0,
        });
      } catch (error) {
        results.errors.push({
          timestamp: Date.now(),
          error: error.message,
          type: error.code || "unknown",
        });
      }

      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  analyzeResults(results) {
    const { requests, errors, startTime, endTime } = results;
    const totalDuration = endTime - startTime;

    const responseTimes = requests.map((r) => r.duration);
    const successfulRequests = requests.filter((r) => r.status < 400);
    const failedRequests = requests.filter((r) => r.status >= 400);

    const analysis = {
      summary: {
        totalRequests: requests.length,
        successfulRequests: successfulRequests.length,
        failedRequests: failedRequests.length + errors.length,
        errorRate: (failedRequests.length + errors.length) / requests.length,
        testDuration: totalDuration,
        throughput: (requests.length / totalDuration) * 1000,
      },
      responseTime: {
        min: Math.min(...responseTimes),
        max: Math.max(...responseTimes),
        mean: responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length,
        p50: this.percentile(responseTimes, 50),
        p90: this.percentile(responseTimes, 90),
        p95: this.percentile(responseTimes, 95),
        p99: this.percentile(responseTimes, 99),
      },
      errors: {
        total: errors.length,
        byType: this.groupBy(errors, "type"),
        timeline: errors.map((e) => ({ timestamp: e.timestamp, type: e.type })),
      },
      recommendations: this.generatePerformanceRecommendations(results),
    };

    this.logResults(analysis);
    return analysis;
  }

  percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil((p / 100) * sorted.length) - 1;
    return sorted[index];
  }

  generatePerformanceRecommendations(results) {
    const recommendations = [];
    const analysis = this.analyzeResults(results);

    if (analysis.responseTime.mean > this.thresholds.responseTime) {
      recommendations.push({
        category: "performance",
        severity: "high",
        issue: "High average response time",
        value: `${analysis.responseTime.mean.toFixed(2)}ms`,
        recommendation: "Optimize database queries and add caching layers",
      });
    }

    if (analysis.summary.throughput < this.thresholds.throughput) {
      recommendations.push({
        category: "scalability",
        severity: "medium",
        issue: "Low throughput",
        value: `${analysis.summary.throughput.toFixed(2)} req/s`,
        recommendation: "Consider horizontal scaling or connection pooling",
      });
    }

    if (analysis.summary.errorRate > this.thresholds.errorRate) {
      recommendations.push({
        category: "reliability",
        severity: "high",
        issue: "High error rate",
        value: `${(analysis.summary.errorRate * 100).toFixed(2)}%`,
        recommendation:
          "Investigate error causes and implement proper error handling",
      });
    }

    return recommendations;
  }

  logResults(analysis) {
    console.log("\nPerformance Test Results:");
    console.log(`Total Requests: ${analysis.summary.totalRequests}`);
    console.log(
      `Success Rate: ${((analysis.summary.successfulRequests / analysis.summary.totalRequests) * 100).toFixed(2)}%`,
    );
    console.log(`Throughput: ${analysis.summary.throughput.toFixed(2)} req/s`);
    console.log(
      `Average Response Time: ${analysis.responseTime.mean.toFixed(2)}ms`,
    );
    console.log(`95th Percentile: ${analysis.responseTime.p95.toFixed(2)}ms`);

    if (analysis.recommendations.length > 0) {
      console.log("\nRecommendations:");
      analysis.recommendations.forEach((rec) => {
        console.log(`- ${rec.issue}: ${rec.recommendation}`);
      });
    }
  }
}

module.exports = { PerformanceTestFramework };
```

### 5. CI/CD Test Integration

Save as `scripts/ci-test-pipeline.yml`:

```yaml
# .github/workflows/test-automation.yml
name: Test Automation Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit -- --coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

      - name: Comment coverage on PR
        uses: romeovs/lcov-reporter-action@v0.3.1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          lcov-file: ./coverage/lcov.info

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run database migrations
        run: npm run db:migrate
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Build application
        run: npm run build

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30

  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run performance tests
        run: npm run test:performance

      - name: Upload performance results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: performance-results/
```

## Testing Best Practices

### Test Organization (AAA Pattern)

```javascript
describe("UserService", () => {
  describe("createUser", () => {
    it("should create user with valid data", async () => {
      // Arrange
      const userData = { email: "test@example.com", name: "Test User" };

      // Act
      const result = await userService.createUser(userData);

      // Assert
      expect(result).toHaveProperty("id");
      expect(result.email).toBe(userData.email);
    });

    it("should throw error with invalid email", async () => {
      // Arrange
      const userData = { email: "invalid-email", name: "Test User" };

      // Act & Assert
      await expect(userService.createUser(userData)).rejects.toThrow(
        "Invalid email",
      );
    });
  });
});
```

### Quality Metrics Tracking

**Coverage Goals:**
- Line coverage: 80%+
- Branch coverage: 75%+
- Function coverage: 80%+
- Statement coverage: 80%+

**Performance Thresholds:**
- Unit tests: < 10ms per test
- Integration tests: < 1s per test
- E2E tests: < 30s per test
- Full suite: < 10 minutes

**Reliability Targets:**
- Test flakiness: < 1%
- Build pass rate: > 95%
- Deployment confidence: > 98%

## Testing Workflow

### Step 1: Test Strategy Planning

1. Identify test scope and critical paths
2. Define quality gates and coverage goals
3. Select appropriate testing frameworks
4. Plan test data management

### Step 2: Test Implementation

1. Write failing tests first (TDD)
2. Implement minimal code to pass
3. Refactor with tests as safety net
4. Add integration and E2E tests

### Step 3: Test Automation

1. Configure test frameworks
2. Set up CI/CD integration
3. Implement parallel test execution
4. Add test reporting and metrics

### Step 4: Continuous Improvement

1. Monitor test suite performance
2. Reduce flaky tests
3. Improve test coverage
4. Optimize test execution time

## Remember

Effective test automation requires:
- Clear test strategy aligned with risk
- Appropriate test pyramid distribution
- Fast, reliable test execution
- Meaningful quality metrics
- Continuous test maintenance
- Integration with development workflow

Focus on tests that provide high confidence at low maintenance cost.
