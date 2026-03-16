# DevLoop Skill for Claude Code

Comprehensive helper skill for working with the DevLoop development observability tool.

## What This Skill Provides

This skill helps you:

1. **Run DevLoop commands** - Quick access to `just analyze`, `just logs`, `just export`, `just run`
2. **Interpret analysis results** - Understand council mode insights, health scores, and recommendations
3. **Analyze development patterns** - Review git activity and Claude session metadata
4. **Develop DevLoop itself** - Navigate hexagonal architecture, BAML schemas, and GKG integration

## Skill Structure

```
skills/devloop/
├── SKILL.md                           # Main skill definition (loaded by Claude Code)
├── README.md                          # This file
├── resources/                         # Reference documentation
│   ├── architecture-patterns.md       # Hexagonal architecture patterns
│   └── baml-quick-reference.md        # BAML schema development guide
└── scripts/                           # Helper scripts
    ├── analyze-branch.sh              # Branch analysis wrapper
    └── check-health.sh                # Environment health check
```

## Quick Start

### Using the Skill

In Claude Code, this skill is automatically available when working in the DevLoop project. Ask questions like:

- "Analyze the current branch with council mode"
- "How do I interpret the health scores from DevLoop analysis?"
- "Explain the hexagonal architecture pattern used in DevLoop"
- "How do I add a new BAML analyst to the council?"
- "What's the difference between GitAdapter and UnifiedAdapter?"

### Running Helper Scripts

Make scripts executable:

```bash
chmod +x skills/devloop/scripts/*.sh
```

Check environment health:

```bash
./skills/devloop/scripts/check-health.sh
```

Analyze a branch with guidance:

```bash
./skills/devloop/scripts/analyze-branch.sh --council feature/my-feature
```

## Resources

### Architecture Patterns

`resources/architecture-patterns.md` provides:

- Hexagonal architecture overview
- Domain model design patterns
- Port definition (trait-based interfaces)
- Adapter implementation examples
- Dependency injection patterns
- Test double creation
- BAML integration patterns
- Error handling strategies
- Graceful degradation (optional components)
- Council pattern (multi-perspective analysis)

**Use this when:**
- Adding new adapters
- Creating test doubles
- Understanding data flow
- Extending DevLoop's capabilities

### BAML Quick Reference

`resources/baml-quick-reference.md` provides:

- BAML file structure and locations
- Naming conventions (PascalCase classes, snake_case fields)
- Type system (basic, optional, arrays, unions)
- Class and function definition patterns
- Client definitions (GPT-4o Mini, GPT-4o, Claude Sonnet)
- Test patterns
- Prompt engineering tips
- Common mistakes to avoid
- DevLoop-specific examples (council analysts)

**Use this when:**
- Creating new BAML functions
- Adding analysts to the council
- Writing BAML tests
- Debugging BAML schemas
- Choosing appropriate LLM models

## When to Use This Skill

### For DevLoop Users

Use this skill when you want to:

- Run branch analysis and understand the results
- Review development patterns and productivity insights
- Export timeline data for custom analysis
- Understand what different council analysts focus on
- Troubleshoot DevLoop setup issues

**Example prompts:**

- "Run council analysis on my current branch"
- "What does a health score of 0.65 mean?"
- "Show me my development patterns from the last week"
- "Explain the difference between Strict Critic and Creative Explorer"

### For DevLoop Developers

Use this skill when you want to:

- Understand DevLoop's architecture
- Add new features (analyzers, adapters, views)
- Create or modify BAML schemas
- Work with GKG integration
- Write tests using the hexagonal architecture

**Example prompts:**

- "How do I add a new BAML analyst to the council?"
- "Explain the data flow from GitAdapter to the TUI"
- "Show me how to create a test double for BranchAggregator"
- "What's the pattern for graceful GKG degradation?"
- "How do I integrate a new data source using an adapter?"

## Key Concepts

### Council Analysis

DevLoop's unique multi-perspective AI analysis:

- **Strict Critic** - Conservative, risk-focused
- **Creative Explorer** - Innovation, opportunities
- **General Analyst** - Balanced assessment
- **Security Reviewer** - Security vulnerabilities
- **Performance Analyst** - Performance implications

Each provides independent insights, all synthesized into a comprehensive view.

### Hexagonal Architecture

DevLoop separates concerns into three layers:

1. **Domain Layer** (`components/src/domain.rs`) - Pure business logic, zero dependencies
2. **Ports** (`components/src/ports.rs`) - Trait-based interfaces
3. **Adapters** (`cli/src/adapters/`) - Infrastructure implementations

This enables testability, flexibility, and clear separation of concerns.

### BAML Integration

BAML (Boundary AI Modeling Language) defines AI functions:

- Type-safe AI function calls
- Schema-driven output validation
- Multiple LLM client support
- Test framework included

### GKG Integration

GitLab Knowledge Graph provides code structure:

- Function and class definitions
- Code reference graph (call sites)
- Repository map (project structure)
- Optional - DevLoop degrades gracefully if unavailable

## Troubleshooting

### "Skill not loading"

Ensure you're in the DevLoop project directory (`/Users/joe/dev/devloop`). Claude Code loads skills from `./skills/` relative to the project root.

### "Can't find helper scripts"

Make scripts executable:

```bash
chmod +x skills/devloop/scripts/*.sh
```

### "BAML examples don't work"

Regenerate the BAML client:

```bash
cd crates/baml
baml-cli generate
```

### "Architecture diagrams are unclear"

View `resources/architecture-patterns.md` for detailed ASCII diagrams and code examples showing data flow through the hexagonal architecture.

## Maintenance

Update this skill when:

- New DevLoop commands are added to `justfile`
- Council analysts are added/removed/modified
- Architecture patterns change (new adapter types, new ports)
- BAML conventions evolve
- GKG integration approach changes
- New best practices emerge

## Version

- **Version:** 1.0.0
- **Created:** 2026-03-15
- **Last Updated:** 2026-03-15
- **Compatible with:** DevLoop main branch (ratatui conversion complete)

## Related Documentation

- Main project: `/Users/joe/dev/devloop/CLAUDE.md`
- BAML rules: `/Users/joe/.claude/rules/baml.md`
- Testing guide: `/Users/joe/dev/devloop/TESTING_CHECKLIST.md`
- Justfile: `/Users/joe/dev/devloop/justfile`

## Contributing

When extending this skill:

1. Update `SKILL.md` with new capabilities
2. Add detailed patterns to `resources/` if needed
3. Create helper scripts in `scripts/` for common tasks
4. Update this README with new sections
5. Increment version number
6. Update "Last Updated" date

## License

Same license as DevLoop project.
