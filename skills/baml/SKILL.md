---
name: baml-standards
description: Expert BAML (BoundaryML) schema design, code review, and test generation following established standards and conventions. Use this whenever users mention BAML, want to design AI functions, create schemas for LLM interactions, generate test cases, or review existing BAML code. Covers class/function/enum design, client configuration, prompt engineering, and comprehensive testing patterns.
---

# BAML Standards & Best Practices

Expert guidance for designing, reviewing, and testing BAML schemas following established conventions.

## When to Use This Skill

Use this skill when the user:
- Mentions "BAML" or "BoundaryML"
- Wants to design schemas for LLM interactions
- Needs to create or improve AI functions
- Asks for test cases for BAML code
- Wants to review existing BAML schemas
- Needs help with client configuration
- Asks about BAML conventions or best practices

## Core Conventions

### Naming Standards

**Classes, Functions, Clients**: PascalCase
```baml
class UserProfile { }
function ExtractData() { }
client CustomGPT4 { }
```

**Fields, Parameters**: snake_case
```baml
class BranchInsight {
  branch_name string
  health_score float
  is_active bool
}
```

**Tests**: snake_case with descriptive names
```baml
test analyze_active_branch { }
test extract_from_complex_document { }
```

### Type Patterns

**Optional fields**: Use `?` suffix
```baml
class Response {
  title string?           // Optional field
  description string?     // May be null/missing
  items TaskItem[]        // Required array
}
```

**Arrays**: Use `[]` suffix
```baml
recommendations string[]
patterns string[]
related_commits string[]
```

**Union types**: For enums or constrained strings
```baml
risk_level "low" | "medium" | "high"
status "pending" | "in_progress" | "complete"
```

**Descriptions**: Always add `@description` for fields
```baml
class CodeAnalysis {
  file_path string @description("Path to the file being analyzed")
  summary string @description("High-level summary of the analysis")
  complexity string @description("Complexity assessment: low, medium, high")
}
```

### File Organization

**Structure by domain/feature**:
```
baml_src/
├── clients.baml          # LLM client configurations
├── generators.baml       # Code generation settings
├── resume.baml           # Resume extraction domain
├── branch_insights.baml  # Git analysis domain
├── devloop.baml          # DevLoop-specific schemas
└── meta.baml            # Meta-schema generation
```

**File header comments**: Explain the file's purpose
```baml
// DevLoop schemas for agent tasks, code analysis, and planning
```

**Section dividers**: For complex files with multiple logical sections
```baml
// ============================================================================
// COMPLEX TEST CASES - Real-world scenarios
// ============================================================================
```

### Client Configuration

**Named clients**: Define reusable clients in `clients.baml`
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

**Inline clients**: For one-off or example code
```baml
function ExtractResume(resume: string) -> Resume {
  client "openai-responses/gpt-5-mini"
  // ...
}
```

**Client selection guidance**:
- Use Mini models (gpt-4o-mini, haiku) for simple extraction/classification
- Use full models (gpt-4o, sonnet) for complex reasoning/generation
- Add retry policies for production functions
- Use fallback/round-robin for reliability

### Function Design

**Standard function structure**:
```baml
// [Brief description of what the function does]
function FunctionName(
  param1: type,
  param2: type,
  optional_param: type?
) -> ReturnType {
  client ClientName
  prompt #"
    [Clear task description]

    [Input data using template variables]
    {{ param1 }}
    {{ param2 }}

    [Instructions for the LLM]

    {{ ctx.output_format }}
  "#
}
```

**Prompt engineering patterns**:

1. **Context first, then task**:
```baml
prompt #"
  You are a development timeline analyst with access to git commit history.

  Branch: {{ branch_name }}
  Recent commits: {{ commits }}

  User question: {{ question }}

  Provide: ...
"#
```

2. **Clear output expectations**:
```baml
prompt #"
  Provide:
  1. Summary (1-2 sentences)
  2. Health score (0.0-1.0) based on:
     - Activity level (recent vs stale)
     - Work patterns (focused vs scattered)
  3. Recommendations (2-4 actionable steps)
  4. Patterns you detect

  {{ ctx.output_format }}
"#
```

3. **Examples in prompts** (when helpful):
```baml
prompt #"
  Examples:
  Input: "OAuth setup, token refresh implementation"
  Output: user_message: "OAuth implementation", task_type: "feature"

  Input: "what was our last convo about?"
  Output: user_message: "recall conversation", task_type: "question"

  {{ ctx.output_format }}
"#
```

4. **Use heredoc for multi-line strings**: `#"..."`
```baml
commits #"
  Initial implementation (1 week ago)
  Bug fixes (3 days ago)
  Final polish (1 day ago)
"#
```

### Test Patterns

**Comprehensive test coverage**:
```baml
// Basic happy path
test analyze_active_branch { }

// Edge cases
test analyze_stale_branch { }
test analyze_abandoned_experiment { }

// Complex scenarios
test analyze_conflicted_branch { }
test analyze_iterative_feature { }

// Insufficient data
test timeline_insufficient_data { }
```

**Descriptive test names**: Indicate what's being tested
```baml
// Good
test extract_debugging_session { }
test meta_healthcare_system { }
test timeline_cross_session_context { }

// Bad
test test1 { }
test branch_test { }
test user_input { }
```

**Test structure**:
```baml
test descriptive_name {
  functions [FunctionName]
  args {
    param1 "value"
    param2 42
    multi_line #"
      Long value spanning
      multiple lines
    "#
  }
}
```

**Multi-function tests**: For schema generation or related functions
```baml
test meta_complete_system {
  functions [GetMetaBamlFunctions, GetMetaBamlClasses, GetMetaBamlEnums]
  args {
    user_input "Build a CRM system"
  }
}
```

## Design Workflows

### 1. Schema Design from Description

When the user provides a description of what they want to extract or generate:

1. **Identify the data structure**:
   - What entities/classes are needed?
   - What fields does each have?
   - What are the relationships?

2. **Design classes**:
   ```baml
   class EntityName {
     field1 type @description("What this field represents")
     field2 type[] @description("Array of items")
     optional_field type? @description("May not always be present")
   }
   ```

3. **Design the function**:
   - Clear input parameters
   - Appropriate return type
   - Well-crafted prompt

4. **Add tests**:
   - Happy path
   - Edge cases
   - Real-world examples

### 2. Code Review & Improvement

When reviewing existing BAML code, check:

**Naming**: Are classes PascalCase and fields snake_case?

**Descriptions**: Does every field have a clear `@description`?

**Types**: Are optional fields marked with `?`? Are arrays `[]`?

**Prompts**:
- Clear context and instructions?
- Good use of template variables?
- Includes `{{ ctx.output_format }}`?

**Tests**:
- Descriptive names?
- Adequate coverage?
- Real-world examples?

**Client selection**:
- Appropriate model for task complexity?
- Retry policy for production?

### 3. Test Generation

When generating tests for existing functions:

1. **Basic scenarios** (2-3 tests):
   - Simple, common use cases
   - Clear expected outputs

2. **Edge cases** (2-3 tests):
   - Empty/minimal input
   - Very long/complex input
   - Ambiguous cases

3. **Complex scenarios** (2-3 tests):
   - Real-world examples
   - Multi-step workflows
   - Cross-domain integration

4. **Error conditions** (1-2 tests):
   - Invalid input
   - Missing required data
   - Insufficient information

## Output Formats

Provide outputs tailored to what the user needs:

### Complete .baml File

When the user wants a ready-to-use file:

```baml
// [File description]

class ClassName {
  field1 type @description("...")
  field2 type @description("...")
}

function FunctionName(input: type) -> ReturnType {
  client ClientName
  prompt #"
    ...
  "#
}

// Tests
test basic_test {
  functions [FunctionName]
  args {
    input "example"
  }
}
```

### Code Suggestions with Explanations

When reviewing or improving code:

```markdown
## Improvements for branch_analysis.baml

### 1. Add field descriptions
**Current**: `branch_name string`
**Suggested**: `branch_name string @description("Name of the branch being analyzed")`
**Why**: Descriptions help both humans and code generation tools understand the schema.

### 2. Mark optional fields
**Current**: `title string`
**Suggested**: `title string?`
**Why**: If the title may not always be present, mark it optional to avoid parsing errors.

### 3. Improve test naming
**Current**: `test test1 { }`
**Suggested**: `test analyze_active_feature_branch { }`
**Why**: Descriptive names make it clear what scenario is being tested.
```

### Step-by-Step Guidance

When the user needs to understand the process:

```markdown
## Designing a BAML Schema for Invoice Extraction

### Step 1: Identify the entities
We need:
- Invoice (top-level class)
- LineItem (for each item on the invoice)
- Vendor (supplier information)

### Step 2: Design the classes
[Show the class definitions]

### Step 3: Create the extraction function
[Show the function]

### Step 4: Add test cases
[Show 3-4 test examples]

### Step 5: Generate and verify
Run `baml generate` to create the client code, then test with:
`baml test invoice_extraction`
```

## Common Patterns

### Data Extraction

```baml
class ExtractedData {
  entity_name string @description("Primary entity identifier")
  confidence float @description("Extraction confidence (0.0-1.0)")
  fields FieldType[] @description("Extracted fields")
  source_refs string[] @description("References to source locations")
}
```

### Classification

```baml
class Classification {
  category string @description("Primary classification category")
  subcategory string? @description("Optional subcategory")
  confidence float @description("Classification confidence (0.0-1.0)")
  reasoning string @description("Explanation of the classification")
}
```

### Analysis with Recommendations

```baml
class Analysis {
  summary string @description("High-level summary")
  score float @description("Numerical score or rating")
  issues string[] @description("Problems or concerns identified")
  recommendations string[] @description("Actionable suggestions")
  metadata Metadata? @description("Additional context")
}
```

### Multi-Step Workflow

```baml
class WorkflowStep {
  step_name string @description("Name of this step")
  status string @description("pending, in_progress, complete, failed")
  result StepResult? @description("Result if completed")
  error string? @description("Error message if failed")
}

class WorkflowResult {
  steps WorkflowStep[] @description("All workflow steps")
  overall_status string @description("Overall workflow status")
  final_output OutputType @description("Final result")
}
```

## Advanced Patterns

### Meta-Schema Generation

For building BAML schemas from descriptions:

```baml
class MetaBamlClass {
  name string @description("Class name (PascalCase)")
  description string @description("What this class represents")
  fields MetaBamlField[] @description("Fields in the class")
}

class MetaBamlField {
  name string @description("Field name (snake_case)")
  type string @description("Field type (string, int, float, bool, array, custom class)")
  optional bool @description("Whether field is optional")
  description string @description("Field description")
}

function GenerateBamlSchema(user_description: string) -> MetaBamlClass[] {
  client CustomGPT5
  prompt #"
    Generate BAML class definitions for:
    {{ user_description }}

    Follow naming conventions:
    - Classes: PascalCase
    - Fields: snake_case
    - All fields need descriptions
    - Mark optional fields appropriately

    {{ ctx.output_format }}
  "#
}
```

### Client Patterns

**Retry policies**:
```baml
retry_policy Exponential {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}

client<llm> RobustClient {
  provider openai-responses
  retry_policy Exponential
  options { ... }
}
```

**Fallback chains**:
```baml
client<llm> ReliableClient {
  provider fallback
  options {
    strategy [PrimaryClient, BackupClient]
  }
}
```

**Round-robin for load balancing**:
```baml
client<llm> BalancedClient {
  provider round-robin
  options {
    strategy [ClientA, ClientB]
  }
}
```

## Quality Checklist

Before finalizing BAML code, verify:

- [ ] All classes use PascalCase naming
- [ ] All fields use snake_case naming
- [ ] All fields have `@description` annotations
- [ ] Optional fields marked with `?`
- [ ] Arrays marked with `[]`
- [ ] Functions have clear, descriptive names
- [ ] Prompts include context before task
- [ ] Prompts end with `{{ ctx.output_format }}`
- [ ] Client selection appropriate for task
- [ ] Tests have descriptive names (not test1, test2)
- [ ] Test coverage includes happy path + edge cases
- [ ] Multi-line strings use heredoc syntax `#"..."`
- [ ] File has header comment explaining purpose
- [ ] Complex files have section dividers

## Common Mistakes to Avoid

1. **Missing descriptions**: Every field should explain what it contains
2. **Wrong naming case**: Don't use camelCase for fields or snake_case for classes
3. **Not marking optionals**: Fields that may be absent need the `?` suffix
4. **Generic test names**: "test1" doesn't indicate what's being tested
5. **No `ctx.output_format`**: Functions need this for proper structured output
6. **Wrong client choice**: Don't use expensive models for simple tasks
7. **No edge case tests**: Only testing happy paths misses important scenarios
8. **Overly complex prompts**: Be clear and concise; don't over-specify
9. **Missing examples in prompts**: Complex tasks benefit from examples
10. **Inconsistent file organization**: Group related functionality together

## Example: Complete Schema Design

Let's design a complete schema for analyzing code pull requests:

```baml
// Pull request analysis for code review automation

class CodeChange {
  file_path string @description("Path to the modified file")
  lines_added int @description("Number of lines added")
  lines_removed int @description("Number of lines removed")
  change_type string @description("Type: added, modified, deleted, renamed")
}

class SecurityIssue {
  severity string @description("Severity: critical, high, medium, low")
  issue_type string @description("Type of security issue")
  location string @description("File and line number")
  description string @description("Description of the issue")
  recommendation string @description("How to fix it")
}

class PullRequestAnalysis {
  summary string @description("High-level summary of the PR")
  impact_assessment string @description("Assessment of the change's impact")
  code_quality_score float @description("Overall code quality (0.0-1.0)")
  security_issues SecurityIssue[] @description("Security concerns identified")
  test_coverage_adequate bool @description("Whether tests are sufficient")
  recommendations string[] @description("Suggestions for improvement")
  approval_recommendation string @description("approve, request_changes, comment")
  reasoning string @description("Explanation for the recommendation")
}

function AnalyzePullRequest(
  title: string,
  description: string,
  changes: string,
  diff_stats: string
) -> PullRequestAnalysis {
  client CustomGPT5
  prompt #"
    You are an expert code reviewer analyzing a pull request.

    PR Title: {{ title }}
    Description: {{ description }}

    File Changes:
    {{ changes }}

    Diff Statistics:
    {{ diff_stats }}

    Analyze this PR for:
    1. Code quality and maintainability
    2. Security vulnerabilities
    3. Test coverage adequacy
    4. Potential bugs or issues
    5. Overall impact and risk

    Provide detailed analysis with specific recommendations.
    For security issues, be thorough and categorize by severity.

    {{ ctx.output_format }}
  "#
}

// Tests
test analyze_feature_addition {
  functions [AnalyzePullRequest]
  args {
    title "feat: add user authentication"
    description "Implements OAuth2 authentication flow with JWT tokens"
    changes #"
      Added:
      - src/auth/oauth.rs (OAuth implementation)
      - src/auth/jwt.rs (JWT token handling)
      Modified:
      - src/main.rs (integrated auth middleware)
    "#
    diff_stats "+245 -12 lines across 3 files"
  }
}

test analyze_security_fix {
  functions [AnalyzePullRequest]
  args {
    title "security: fix SQL injection vulnerability"
    description "Replace string concatenation with parameterized queries"
    changes #"
      Modified:
      - src/db/queries.rs (parameterized all SQL queries)
      Added:
      - tests/security/sql_injection_test.rs
    "#
    diff_stats "+89 -45 lines across 2 files"
  }
}

test analyze_refactoring {
  functions [AnalyzePullRequest]
  args {
    title "refactor: extract duplicated validation logic"
    description "DRY principle - consolidate repeated validation into shared module"
    changes #"
      Added:
      - src/validation/common.rs
      Modified:
      - src/api/users.rs
      - src/api/posts.rs
      - src/api/comments.rs
    "#
    diff_stats "+120 -180 lines across 4 files"
  }
}
```

This example demonstrates:
- Clear class hierarchy
- Comprehensive field descriptions
- Appropriate types (strings, ints, bools, arrays, floats)
- Well-structured function with clear prompt
- Three diverse test cases covering different PR scenarios

When designing schemas, always think about:
1. What data needs to be captured?
2. How will it be used?
3. What edge cases exist?
4. How can we make it extensible for future needs?
