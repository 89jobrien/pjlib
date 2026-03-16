# BAML Quick Reference for DevLoop

Fast reference for working with BAML schemas in DevLoop.

## File Locations

```
crates/baml/
├── baml_src/          # Source BAML files (edit these)
│   ├── analysis.baml  # Branch analysis functions
│   ├── clients.baml   # LLM client definitions
│   └── types.baml     # Domain type definitions
├── baml_client/       # Generated Rust code (don't edit!)
│   ├── mod.rs
│   └── ...
└── Cargo.toml
```

## Regenerate BAML Client

After editing `.baml` files:

```bash
cd crates/baml
baml-cli generate
```

Or from project root:

```bash
just baml-generate  # If you add this to justfile
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `BranchInsight`, `UserProfile` |
| Functions | PascalCase | `AnalyzeBranch`, `ExtractData` |
| Clients | PascalCase | `CustomGPT5Mini`, `CustomSonnet4` |
| Fields | snake_case | `branch_name`, `health_score` |
| Parameters | snake_case | `commit_count`, `session_count` |
| Tests | snake_case | `test_analyze_active_branch` |

## Type System

### Basic Types

```baml
string       // Text
int          // Integer
float        // Floating point
bool         // Boolean
```

### Optional Types

```baml
field_name string?    // May be null
field_name int?       // May be null
```

### Arrays

```baml
items string[]        // Array of strings
scores float[]        // Array of floats
insights BranchInsight[]  // Array of custom types
```

### Union Types (Enums)

```baml
status "pending" | "in_progress" | "complete"
risk_level "low" | "medium" | "high"
priority "p0" | "p1" | "p2" | "p3"
```

## Class Definition Pattern

```baml
class BranchInsight {
  branch_name string @description("Name of the git branch being analyzed")
  health_score float @description("Overall health score from 0.0 (poor) to 1.0 (excellent)")
  risk_level "low" | "medium" | "high" @description("Risk level assessment")
  insights string[] @description("Array of specific observations and findings")
  recommendations string[] @description("Array of actionable suggestions for improvement")
  analyst_role string @description("Role of the analyst providing this insight")
}
```

**Key points:**
- Every field needs `@description`
- Use union types for constrained strings
- Arrays use `[]` suffix
- Optional fields use `?` suffix

## Function Definition Pattern

```baml
function AnalyzeBranch_StrictCritic(
  branch_name: string
  commits: string
  sessions: string
  commit_count: int
  session_count: int
) -> BranchInsight {
  client CustomGPT5Mini
  prompt #"
    You are a STRICT CRITIC reviewing a development branch.
    Your role is to identify risks, issues, and potential problems.

    Branch: {{ branch_name }}
    Total commits: {{ commit_count }}
    Total sessions: {{ session_count }}

    Recent commit messages:
    {{ commits }}

    Recent session summaries:
    {{ sessions }}

    Provide a conservative risk assessment focusing on:
    - Code quality concerns
    - Potential bugs or issues
    - Missing tests or documentation
    - Technical debt
    - Security vulnerabilities

    {{ ctx.output_format }}
  "#
}
```

**Key points:**
- Function name is PascalCase
- Parameters are snake_case with type annotations
- Return type specified after `->`
- `client` specifies which LLM to use
- `prompt` uses heredoc syntax `#"..."#`
- Always end with `{{ ctx.output_format }}`
- Template variables use `{{ variable_name }}`

## Client Definitions

### GPT-4o Mini (Fast, Cheap)

```baml
client<llm> CustomGPT5Mini {
  provider openai-responses
  retry_policy Exponential
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
  }
}
```

**Use for:**
- Simple extraction
- Classification tasks
- Quick analyses
- High-volume operations

### GPT-4o (Standard)

```baml
client<llm> CustomGPT5 {
  provider openai-responses
  retry_policy Exponential
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}
```

**Use for:**
- Complex reasoning
- Detailed analysis
- Creative tasks
- Quality-critical operations

### Claude Sonnet (Alternative)

```baml
client<llm> CustomSonnet4 {
  provider anthropic
  retry_policy Exponential
  options {
    model "claude-sonnet-4"
    api_key env.ANTHROPIC_API_KEY
  }
}
```

**Use for:**
- Code analysis
- Technical writing
- Architecture decisions

### Retry Policy

```baml
retry_policy Exponential {
  max_retries 3
  strategy {
    type exponential_backoff
  }
}
```

## Test Pattern

```baml
test analyze_active_feature_branch {
  functions [AnalyzeBranch_StrictCritic]
  args {
    branch_name "feature/auth-refactor"
    commits #"
      Refactor OAuth flow (3 days ago)
      Add token refresh logic (2 days ago)
      Fix edge case in logout (1 day ago)
    "#
    sessions #"
      Planning auth refactor (4 days ago)
      Implementing OAuth (2 days ago)
    "#
    commit_count 5
    session_count 2
  }
}
```

**Key points:**
- Test name is snake_case and descriptive
- `functions` array lists which functions to test
- `args` provides test inputs
- Use heredoc `#"..."#` for multi-line strings
- Include diverse test cases (happy path, edge cases)

## Common BAML Patterns in DevLoop

### Pattern 1: Multi-Role Analysis

```baml
// Define base insight type
class BranchInsight {
  branch_name string @description("Branch name")
  health_score float @description("Score 0.0-1.0")
  risk_level "low" | "medium" | "high" @description("Risk assessment")
  insights string[] @description("Observations")
  recommendations string[] @description("Suggestions")
  analyst_role string @description("Analyst role name")
}

// Define function for each role
function AnalyzeBranch_StrictCritic(...) -> BranchInsight { ... }
function AnalyzeBranch_CreativeExplorer(...) -> BranchInsight { ... }
function AnalyzeBranch_GeneralAnalyst(...) -> BranchInsight { ... }
function AnalyzeBranch_SecurityReviewer(...) -> BranchInsight { ... }
function AnalyzeBranch_PerformanceAnalyst(...) -> BranchInsight { ... }

// Synthesize multiple insights
function SynthesizeCouncilInsights(
  insights: BranchInsight[]
) -> CouncilSynthesis {
  client CustomGPT5
  prompt #"
    You are a meta-analyst synthesizing insights from multiple reviewers.

    {% for insight in insights %}
    ## {{ insight.analyst_role }}
    Health Score: {{ insight.health_score }}
    Risk Level: {{ insight.risk_level }}

    Insights:
    {% for item in insight.insights %}
    - {{ item }}
    {% endfor %}

    Recommendations:
    {% for item in insight.recommendations %}
    - {{ item }}
    {% endfor %}
    {% endfor %}

    Synthesize into a coherent final assessment.

    {{ ctx.output_format }}
  "#
}

class CouncilSynthesis {
  overall_health_score float @description("Aggregate health score")
  consensus_risk_level "low" | "medium" | "high" @description("Consensus risk")
  key_insights string[] @description("Most important insights across all analysts")
  priority_recommendations string[] @description("Highest priority actions")
  dissenting_opinions string[] @description("Significant disagreements between analysts")
}
```

### Pattern 2: Progressive Enhancement

```baml
// Base analysis (minimal data)
function AnalyzeBranch_Basic(
  branch_name: string
  commit_count: int
) -> BasicInsight {
  client CustomGPT5Mini
  prompt #"
    Quick health check for {{ branch_name }} with {{ commit_count }} commits.
    {{ ctx.output_format }}
  "#
}

// Enhanced analysis (with git data)
function AnalyzeBranch_Enhanced(
  branch_name: string
  commits: string
  commit_count: int
) -> EnhancedInsight {
  client CustomGPT5Mini
  prompt #"
    Analyze {{ branch_name }}:
    {{ commits }}
    {{ ctx.output_format }}
  "#
}

// Full analysis (with git + session data)
function AnalyzeBranch_Full(
  branch_name: string
  commits: string
  sessions: string
  commit_count: int
  session_count: int
) -> FullInsight {
  client CustomGPT5
  prompt #"
    Comprehensive analysis of {{ branch_name }}:

    Commits ({{ commit_count }}):
    {{ commits }}

    Sessions ({{ session_count }}):
    {{ sessions }}

    {{ ctx.output_format }}
  "#
}
```

### Pattern 3: Conditional Context

```baml
function AnalyzeBranch_WithOptionalGKG(
  branch_name: string
  commits: string
  sessions: string
  commit_count: int
  session_count: int
  code_structure: string?  // Optional GKG data
) -> BranchInsight {
  client CustomGPT5
  prompt #"
    Analyze branch: {{ branch_name }}

    Commits: {{ commits }}
    Sessions: {{ sessions }}

    {% if code_structure %}
    Code Structure (from GKG):
    {{ code_structure }}

    Use code structure to enhance your analysis.
    {% else %}
    Note: Code structure data unavailable.
    {% endif %}

    {{ ctx.output_format }}
  "#
}
```

## Prompt Engineering Tips

### 1. Clear Role Definition

```baml
prompt #"
  You are a SECURITY REVIEWER for a development branch.
  Your primary focus is identifying security vulnerabilities and risks.

  [rest of prompt]
"#
```

### 2. Structured Input

```baml
prompt #"
  Branch: {{ branch_name }}
  Total commits: {{ commit_count }}
  Total sessions: {{ session_count }}

  Recent commit messages:
  {{ commits }}

  Recent session summaries:
  {{ sessions }}

  [analysis instructions]
"#
```

### 3. Explicit Output Focus

```baml
prompt #"
  [input context]

  Focus your analysis on:
  - Code quality and maintainability
  - Test coverage
  - Documentation completeness
  - Performance implications

  [output format]
"#
```

### 4. Template Loops

```baml
prompt #"
  {% for commit in commits %}
  Commit {{ loop.index }}: {{ commit }}
  {% endfor %}
"#
```

### 5. Conditional Sections

```baml
prompt #"
  {% if session_count > 0 %}
  Sessions indicate active development with AI assistance.
  {% else %}
  No AI sessions detected - manual development.
  {% endif %}
"#
```

## Common Mistakes

### ❌ Wrong Naming

```baml
// Bad
class branchInsight { ... }        // Should be PascalCase
function analyze_branch() { ... }  // Should be PascalCase
test TestOne { ... }               // Should be snake_case

// Good
class BranchInsight { ... }
function AnalyzeBranch() { ... }
test analyze_active_branch { ... }
```

### ❌ Missing Descriptions

```baml
// Bad
class BranchInsight {
  branch_name string
  health_score float
}

// Good
class BranchInsight {
  branch_name string @description("Name of the git branch")
  health_score float @description("Health score from 0.0 to 1.0")
}
```

### ❌ Missing Output Format

```baml
// Bad
prompt #"
  Analyze this branch:
  {{ commits }}
"#

// Good
prompt #"
  Analyze this branch:
  {{ commits }}

  {{ ctx.output_format }}
"#
```

### ❌ Wrong Model for Task

```baml
// Bad - expensive model for simple task
function ExtractBranchName(text: string) -> string {
  client CustomGPT5  // Overkill
  prompt #"..."#
}

// Good - cheap model for simple task
function ExtractBranchName(text: string) -> string {
  client CustomGPT5Mini  // Appropriate
  prompt #"..."#
}
```

## Debugging BAML

### Check Generated Code

```bash
# After generating, check the Rust code
cat crates/baml/baml_client/mod.rs
```

### Test Individual Functions

```bash
# Run BAML tests
cd crates/baml
baml-cli test

# Run specific test
baml-cli test test_analyze_active_branch
```

### Enable BAML Logging

```bash
# In Rust code
std::env::set_var("BAML_LOG", "debug");

# Or in shell
export BAML_LOG=debug
just analyze
```

### Validate Schema

```bash
cd crates/baml
baml-cli validate
```

## DevLoop-Specific Examples

### Current Council Analysts

1. **Strict Critic** - `AnalyzeBranch_StrictCritic`
   - Focus: Risks, issues, conservative assessment
   - Use: Before merging critical branches

2. **Creative Explorer** - `AnalyzeBranch_CreativeExplorer`
   - Focus: Innovation, opportunities, alternative approaches
   - Use: For feature branches, brainstorming

3. **General Analyst** - `AnalyzeBranch_GeneralAnalyst`
   - Focus: Balanced view, overall health
   - Use: Default analysis, general assessment

4. **Security Reviewer** - `AnalyzeBranch_SecurityReviewer`
   - Focus: Security vulnerabilities, auth issues
   - Use: Branches touching authentication, data handling

5. **Performance Analyst** - `AnalyzeBranch_PerformanceAnalyst`
   - Focus: Performance bottlenecks, optimization
   - Use: Branches with algorithms, large data processing

### Adding a New Analyst

```baml
// 1. Define function in analysis.baml
function AnalyzeBranch_DocsReviewer(
  branch_name: string
  commits: string
  sessions: string
  commit_count: int
  session_count: int
) -> BranchInsight {
  client CustomGPT5Mini
  prompt #"
    You are a DOCUMENTATION REVIEWER for development branches.

    Focus on:
    - README updates and completeness
    - Code comments and docstrings
    - API documentation
    - User-facing documentation
    - Changelog entries

    Branch: {{ branch_name }}
    Commits ({{ commit_count }}):
    {{ commits }}

    Sessions ({{ session_count }}):
    {{ sessions }}

    Assess documentation quality and completeness.

    {{ ctx.output_format }}
  "#
}

// 2. Add test
test analyze_docs_focused_branch {
  functions [AnalyzeBranch_DocsReviewer]
  args {
    branch_name "feature/api-docs"
    commits #"
      Add OpenAPI spec (2 days ago)
      Update README with examples (1 day ago)
      Add code comments to main.rs (today)
    "#
    sessions #"
      Planning documentation structure (3 days ago)
    "#
    commit_count 3
    session_count 1
  }
}

// 3. Regenerate
// $ cd crates/baml && baml-cli generate

// 4. Update CouncilAdapter in Rust
// Add AnalystRole::DocsReviewer to council members
```

## Quick Checklist

Before committing BAML changes:

- [ ] Class names are PascalCase
- [ ] Field names are snake_case
- [ ] All fields have `@description`
- [ ] Functions end with `{{ ctx.output_format }}`
- [ ] Tests are descriptive snake_case
- [ ] Appropriate client selected (Mini vs. Full)
- [ ] Optional fields marked with `?`
- [ ] Arrays marked with `[]`
- [ ] Regenerated client: `baml-cli generate`
- [ ] Tests pass: `baml-cli test`

## Resources

- **BAML Docs**: https://docs.boundaryml.com/
- **DevLoop BAML Rules**: `/Users/joe/.claude/rules/baml.md`
- **DevLoop BAML Source**: `/Users/joe/dev/devloop/crates/baml/baml_src/`
- **Generated Client**: `/Users/joe/dev/devloop/crates/baml/baml_client/`
