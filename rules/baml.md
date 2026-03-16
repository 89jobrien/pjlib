# BAML File Rules

## Naming Conventions

- **Classes, Functions, Clients**: PascalCase
  ```baml
  // Good
  class UserProfile { }
  function ExtractData() { }
  client CustomGPT4 { }

  // Bad
  class user_profile { }
  function extract_data() { }
  client custom_gpt4 { }
  ```

- **Fields, Parameters**: snake_case
  ```baml
  // Good
  class BranchInsight {
    branch_name string
    health_score float
    is_active bool
  }

  // Bad
  class BranchInsight {
    branchName string
    healthScore float
    isActive bool
  }
  ```

- **Tests**: snake_case with descriptive names
  ```baml
  // Good
  test analyze_active_branch { }
  test extract_from_complex_document { }

  // Bad
  test test1 { }
  test analyzeActiveBranch { }
  ```

## Type Annotations

- **Optional fields**: Use `?` suffix
  ```baml
  // Good
  class Response {
    title string?        // May be null
    items Item[]         // Required array
  }

  // Bad
  class Response {
    title string         // Should be optional
    items Item           // Should be array
  }
  ```

- **Arrays**: Use `[]` suffix
  ```baml
  recommendations string[]
  related_commits string[]
  ```

- **Descriptions**: Always include `@description`
  ```baml
  // Good
  class Analysis {
    file_path string @description("Path to the file being analyzed")
    score float @description("Quality score from 0.0 to 1.0")
  }

  // Bad
  class Analysis {
    file_path string
    score float
  }
  ```

- **Union types**: For enums or constrained strings
  ```baml
  status "pending" | "in_progress" | "complete"
  risk_level "low" | "medium" | "high"
  ```

## File Organization

- Add file header comments explaining purpose
- Use section dividers for complex files:
  ```baml
  // ============================================================================
  // SECTION NAME
  // ============================================================================
  ```
- Group related classes, functions, and tests together

## Function Design

- **Heredoc syntax** for multi-line prompts:
  ```baml
  // Good
  function Analyze(code: string) -> Analysis {
    client CustomGPT5Mini
    prompt #"
      Analyze this code:
      {{ code }}

      {{ ctx.output_format }}
    "#
  }

  // Bad - no heredoc, missing ctx.output_format
  function Analyze(code: string) -> Analysis {
    client CustomGPT5Mini
    prompt "Analyze: {{ code }}"
  }
  ```

- **Always end prompts** with `{{ ctx.output_format }}`
  ```baml
  prompt #"
    Your task here...

    {{ ctx.output_format }}
  "#
  ```

- **Use descriptive client names** from clients.baml
  ```baml
  // Good
  client CustomGPT5Mini
  client CustomSonnet4

  // Bad - inline clients should only be for examples
  client "openai/gpt-4"
  ```

- **Include clear context** before task in prompts
  ```baml
  // Good
  prompt #"
    You are a code analyst reviewing pull requests.

    PR Title: {{ title }}
    Files Changed: {{ files }}

    Analyze for security issues and code quality.
    {{ ctx.output_format }}
  "#

  // Bad - no context
  prompt #"
    {{ title }}
    {{ files }}
    {{ ctx.output_format }}
  "#
  ```

## Client Selection

- **Use Mini models** for simple extraction/classification:
  ```baml
  // Good - simple extraction
  function ExtractEmail(text: string) -> string {
    client CustomGPT5Mini  // Fast and cheap
    prompt #"..." "#
  }

  // Bad - overkill for simple task
  function ExtractEmail(text: string) -> string {
    client CustomGPT5  // Too expensive
    prompt #"..." "#
  }
  ```

- **Use full models** for complex reasoning:
  ```baml
  // Good - complex analysis needs powerful model
  function AnalyzeArchitecture(codebase: string) -> DetailedAnalysis {
    client CustomGPT5  // or CustomSonnet4
    prompt #"..." "#
  }
  ```

- **Add retry policies** for production:
  ```baml
  client<llm> RobustClient {
    provider openai-responses
    retry_policy Exponential  // Defined in clients.baml
    options {
      model "gpt-4o-mini"
      api_key env.OPENAI_API_KEY
    }
  }
  ```

- **Define clients in clients.baml** for reusability:
  ```baml
  // clients.baml
  client<llm> CustomGPT5Mini {
    provider openai-responses
    retry_policy Exponential
    options {
      model "gpt-4o-mini"
      api_key env.OPENAI_API_KEY
    }
  }

  // usage.baml
  function MyFunction(input: string) -> Output {
    client CustomGPT5Mini  // Reuse defined client
    prompt #"..." "#
  }
  ```

## Test Patterns

- **Descriptive test names** indicating what's tested:
  ```baml
  // Good
  test analyze_active_feature_branch { }
  test extract_from_multi_currency_invoice { }
  test classify_security_fix_commit { }

  // Bad
  test test1 { }
  test test_function { }
  test my_test { }
  ```

- **Include diverse scenarios**:
  ```baml
  // Happy path
  test extract_simple_resume { }

  // Edge cases
  test extract_resume_missing_email { }
  test extract_resume_with_special_characters { }

  // Complex scenarios
  test extract_multilingual_resume { }
  test extract_resume_with_multiple_jobs { }
  ```

- **Use heredoc** for multi-line test arguments:
  ```baml
  test analyze_complex_branch {
    functions [AnalyzeBranch]
    args {
      branch_name "feature/auth"
      commits #"
        OAuth setup (3 days ago)
        Token refresh (2 days ago)
        Bug fixes (1 day ago)
      "#
      sessions #"
        Planning (4 days ago)
        Implementation (2 days ago)
      "#
      commit_count 5
      session_count 2
    }
  }
  ```

## Quality Standards

Before committing .baml files:

- [ ] All classes use PascalCase
- [ ] All fields use snake_case
- [ ] All fields have @description
- [ ] Optional fields marked with ?
- [ ] Arrays marked with []
- [ ] Tests have descriptive names
- [ ] Prompts end with {{ ctx.output_format }}
- [ ] File has header comment
- [ ] Client selection is appropriate

## Common Mistakes to Avoid

- Don't use camelCase for fields or snake_case for classes
- Don't forget @description annotations
- Don't use generic test names (test1, test2)
- Don't skip {{ ctx.output_format }} in function prompts
- Don't use expensive models for simple tasks
- Don't only test happy paths - include edge cases
