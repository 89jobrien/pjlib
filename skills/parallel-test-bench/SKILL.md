---
name: parallel-test-bench
description: Infrastructure for running parallel agent tests with automatic metric collection, programmatic grading, and benchmark aggregation. Use this skill when the user wants to A/B test different approaches, compare agent configurations, benchmark performance improvements, run parallel experiments, or test multiple variations of a prompt or implementation. Trigger for phrases like "test in parallel", "compare approaches", "benchmark", "A/B test", "run experiments", or when the user wants to collect timing/token metrics from multiple agent runs.
---

# Parallel Test Bench

You are an expert at designing and running parallel agent experiments with automatic metric collection and benchmark aggregation.

## When to Use This Skill

Use this skill whenever you need to:
- Compare multiple approaches or implementations side-by-side
- A/B test different prompts, tools, or configurations
- Benchmark performance improvements (before/after comparisons)
- Run experiments with different agent settings
- Collect timing and token usage metrics systematically
- Generate comparison reports with statistical analysis

## Core Workflow

The parallel testing workflow has 5 phases:

1. **Setup** - Define test configurations and create workspace structure
2. **Spawn** - Launch all agents in parallel (one message, multiple Agent tool calls)
3. **Collect** - Capture timing/token metrics from task notifications
4. **Grade** - Evaluate outputs against assertions programmatically
5. **Aggregate** - Generate benchmark reports with comparisons

## Phase 1: Setup

### Define Test Configurations

Before spawning agents, clarify with the user:

**Test name:** What are you testing? (e.g., "emoji-removal", "refactoring-approach")

**Configurations:** What variations to test?
- **Baseline:** The control group (e.g., no skill, old version, simple approach)
- **Treatment:** The experimental group (e.g., with skill, new version, optimized approach)
- Can have 2+ configurations (e.g., baseline vs approach-A vs approach-B)

**Test cases:** What specific tasks to run?
- Each test case needs: prompt, expected output description, optional input files
- Aim for 2-3 test cases minimum
- Each case tests a different aspect or edge case

**Success criteria:** How to measure success?
- Quantitative: assertions that can be checked programmatically
- Qualitative: aspects requiring human judgment

### Create Workspace Structure

```
<test-name>-workspace/
└── iteration-1/
    ├── test-case-1/
    │   ├── baseline/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── treatment/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    ├── test-case-2/
    │   └── ...
    ├── benchmark.json
    └── benchmark.md
```

Don't create all directories upfront - create them as you go when saving outputs.

## Phase 2: Spawn Agents in Parallel

**CRITICAL:** Spawn ALL agents in a SINGLE message using multiple Agent tool calls. This ensures they run truly in parallel.

For each test case, spawn one agent per configuration:

```markdown
Test Case: <descriptive-name>

Baseline agent:
- Configuration: <baseline description>
- Task: <test prompt>
- Save outputs to: workspace/iteration-1/<test-case>/baseline/outputs/

Treatment agent:
- Configuration: <treatment description>
- Task: <same test prompt>
- Save outputs to: workspace/iteration-1/<test-case>/treatment/outputs/
```

**Example agent spawning (all in one message):**

```
I'm spawning 4 agents in parallel (2 test cases × 2 configurations):
```

Then use 4 Agent tool calls in the same response.

### Agent Prompt Template

Each agent should receive clear instructions:

```
Execute this task:
- Configuration: <config description, e.g., "without emoji-remover skill" or "with skill at path/to/skill">
- Task: <user's test prompt>
- Input files: <paths to input files, or "none">
- Save all outputs to: <workspace-path>/outputs/
- Outputs to save: <what matters - e.g., "the cleaned markdown file", "the refactored code">
```

## Phase 3: Collect Metrics

When each agent completes, you receive a task notification with:
- `total_tokens`: Token count
- `duration_ms`: Execution time in milliseconds

**Save this data IMMEDIATELY** - it's only available in the notification:

```json
{
  "total_tokens": 18534,
  "duration_ms": 16408,
  "total_duration_seconds": 16.4
}
```

Save to `<test-case>/<config>/timing.json`.

### Tracking Completions

As agents complete, keep a mental checklist:
- [ ] test-case-1/baseline - tokens: X, time: Ys
- [ ] test-case-1/treatment - tokens: X, time: Ys
- [ ] test-case-2/baseline - tokens: X, time: Ys
- [ ] test-case-2/treatment - tokens: X, time: Ys

Once all complete, proceed to grading.

## Phase 4: Grade Outputs

For each configuration output, evaluate against assertions.

### Programmatic Grading

Use the bundled grading script for objective checks:

```bash
python scripts/grade_outputs.py \
  --test-case <path-to-test-case-dir> \
  --config baseline \
  --assertions <assertions-json>
```

Or write custom grading logic inline:

```python
# Example: Check no emojis remaining
import re
EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001F9FF]')
with open(output_file) as f:
    content = f.read()
has_emojis = bool(EMOJI_PATTERN.search(content))

grading = {
  "expectations": [
    {
      "text": "No emojis in output",
      "passed": not has_emojis,
      "evidence": f"Found {len(EMOJI_PATTERN.findall(content))} emojis" if has_emojis else "Clean"
    }
  ]
}
```

Save to `<test-case>/<config>/grading.json`.

### Grading Schema

```json
{
  "expectations": [
    {
      "text": "Assertion description",
      "passed": true,
      "evidence": "Supporting details"
    }
  ]
}
```

**Field requirements:**
- `text`: Human-readable assertion name
- `passed`: Boolean result
- `evidence`: Why it passed/failed

## Phase 5: Aggregate Results

Use the bundled aggregation script:

```bash
python scripts/aggregate_benchmark.py \
  --workspace workspace/iteration-1 \
  --configs baseline treatment \
  --test-name "emoji-removal"
```

This generates:
- `benchmark.json` - Machine-readable metrics
- `benchmark.md` - Human-readable report

### Benchmark Contents

**Pass Rate:** Percentage of assertions passed per configuration
**Token Usage:** Mean ± stddev across test cases
**Execution Time:** Mean ± stddev across test cases
**Delta:** Difference between configurations (treatment - baseline)

### Manual Aggregation

If you need to aggregate manually:

```python
import json, statistics

configs = {}
for config in ['baseline', 'treatment']:
    grades, tokens, times = [], [], []

    for test_case in test_cases:
        # Load grading
        with open(f"{test_case}/{config}/grading.json") as f:
            g = json.load(f)
            passed = sum(1 for e in g['expectations'] if e['passed'])
            total = len(g['expectations'])
            grades.append(passed / total)

        # Load timing
        with open(f"{test_case}/{config}/timing.json") as f:
            t = json.load(f)
            tokens.append(t['total_tokens'])
            times.append(t['total_duration_seconds'])

    configs[config] = {
        'pass_rate': {'mean': statistics.mean(grades), 'values': grades},
        'tokens': {'mean': statistics.mean(tokens), 'stddev': statistics.stdev(tokens) if len(tokens) > 1 else 0},
        'time': {'mean': statistics.mean(times), 'stddev': statistics.stdev(times) if len(times) > 1 else 0}
    }

# Calculate deltas
delta = {
    'pass_rate': configs['treatment']['pass_rate']['mean'] - configs['baseline']['pass_rate']['mean'],
    'tokens': configs['treatment']['tokens']['mean'] - configs['baseline']['tokens']['mean'],
    'time': configs['treatment']['time']['mean'] - configs['baseline']['time']['mean']
}
```

## Reporting Results

After aggregation, present findings to the user:

### Summary Format

```markdown
# <Test Name> - Benchmark Results

## Summary
- Test Cases: N
- Configurations: baseline vs treatment

## Results

### Pass Rate
- Baseline: X.X%
- Treatment: Y.Y%
- Delta: +Z.Z% (better/worse/same)

### Token Usage
- Baseline: X,XXX ± YYY tokens
- Treatment: X,XXX ± YYY tokens
- Delta: +Z,ZZZ tokens (X% increase/decrease)

### Execution Time
- Baseline: XX.X ± Y.Y seconds
- Treatment: XX.X ± Y.Y seconds
- Delta: +Z.Z seconds (X% faster/slower)

## Analysis

<Your interpretation of the results>

## Recommendation

<What the data suggests - e.g., "Treatment approach is 15% faster with same quality" or "Baseline is simpler and equally effective">
```

## Advanced: Multi-Configuration Testing

For 3+ configurations (e.g., baseline vs approach-A vs approach-B vs approach-C):

1. **Spawn N×M agents** (N test cases × M configurations)
2. **Collect metrics for all**
3. **Grade all outputs**
4. **Aggregate with pairwise comparisons:**
   - Compare each treatment to baseline
   - Optionally compare treatments to each other
5. **Report best performer** with statistical significance

## Best Practices

### Choosing Test Cases

**Good test cases:**
- Representative of real-world usage
- Test different aspects (edge cases, common cases, stress tests)
- Have clear success criteria

**Poor test cases:**
- Too similar to each other (test the same thing)
- Trivial (any approach works)
- Ambiguous success criteria

### Fair Comparisons

**Ensure apples-to-apples:**
- Same prompt for all configurations
- Same input files
- Same model (unless testing model differences)
- Run truly in parallel (not sequentially)

### Statistical Rigor

**For small sample sizes (2-3 test cases):**
- Report individual results, not just averages
- Be cautious about generalizing
- Consider variance (stddev) when interpreting means

**For larger sample sizes (10+ test cases):**
- Use statistical tests (t-tests, confidence intervals)
- Report effect sizes, not just p-values
- Consider practical significance vs statistical significance

## Common Use Cases

### Use Case 1: Skill Effectiveness Testing

**Question:** Does this skill improve results?

**Setup:**
- Baseline: Without skill
- Treatment: With skill
- Test cases: 3-5 representative tasks

**Metrics:**
- Quality: Pass rate on assertions
- Efficiency: Token usage, execution time
- Consistency: Stddev across test cases

### Use Case 2: Prompt Optimization

**Question:** Which prompt variant works best?

**Setup:**
- Baseline: Original prompt
- Treatment-A: Variant with examples
- Treatment-B: Variant with reasoning steps
- Treatment-C: Variant with constraints

**Metrics:**
- Correctness: Did it produce the right output?
- Completeness: Did it address all requirements?
- Clarity: Is the output easy to understand?

### Use Case 3: Refactoring Validation

**Question:** Did refactoring break anything?

**Setup:**
- Baseline: Old implementation
- Treatment: Refactored implementation
- Test cases: Comprehensive test suite

**Metrics:**
- Correctness: All tests pass
- Performance: Execution time
- Code quality: Complexity, readability (manual assessment)

### Use Case 4: Model Comparison

**Question:** Which model is best for this task?

**Setup:**
- Baseline: Sonnet
- Treatment-A: Opus
- Treatment-B: Haiku

**Metrics:**
- Quality: Task-specific assertions
- Cost: Token usage × model pricing
- Speed: Execution time

## Bundled Scripts

The skill includes helper scripts in `scripts/`:

### grade_outputs.py

Programmatic grading helper:

```bash
python scripts/grade_outputs.py \
  --output-dir <path-to-outputs> \
  --assertions <assertions-json-file> \
  --save-to <grading-json-path>
```

### aggregate_benchmark.py

Benchmark aggregation:

```bash
python scripts/aggregate_benchmark.py \
  --workspace <iteration-dir> \
  --configs baseline treatment \
  --test-name "my-test"
```

### compare_outputs.py

Detailed diff generation for outputs:

```bash
python scripts/compare_outputs.py \
  --baseline <baseline-output> \
  --treatment <treatment-output> \
  --format <text|json|md>
```

## Workflow Checklist

Use this checklist for each test run:

**Setup Phase:**
- [ ] Define test name and configurations
- [ ] Create workspace structure
- [ ] Define test cases with clear prompts
- [ ] Define assertions for grading

**Execution Phase:**
- [ ] Spawn all agents in parallel (single message, multiple Agent calls)
- [ ] Monitor agent completions
- [ ] Save timing.json for each completion immediately

**Analysis Phase:**
- [ ] Grade all outputs against assertions
- [ ] Save grading.json for each configuration
- [ ] Aggregate results into benchmark.json
- [ ] Generate benchmark.md report

**Reporting Phase:**
- [ ] Present summary to user
- [ ] Explain key findings
- [ ] Make recommendation based on data

## Remember

The goal is to provide **objective, data-driven comparisons** that help the user make informed decisions. Focus on:

1. **Fair tests** - Same conditions for all configurations
2. **Meaningful metrics** - Measure what actually matters
3. **Clear reporting** - Present results understandably
4. **Actionable insights** - What should the user do with this data?

Avoid:
- Spawning agents sequentially (defeats the purpose of parallel testing)
- Forgetting to capture timing data (only available in task notification)
- Making claims without statistical backing
- Testing configurations that differ in multiple ways (can't isolate cause)
