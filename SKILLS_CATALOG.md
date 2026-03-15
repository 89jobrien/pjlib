# Claude Code Skills Catalog

*Generated from 18 skills*

---

## Statistics

- **Total Skills:** 18
- **Categories:** 2

**Most Used Tools:**
- `Read`: 11 skills
- `Bash`: 11 skills
- `Grep`: 9 skills
- `Glob`: 9 skills
- `Edit`: 5 skills

---

## Skills by Category

### General

- **ai-slop-remover**: Remove AI-generated code slop by comparing current branch against base branch an...
- **baml-standards**: Expert BAML (BoundaryML) schema design, code review, and test generation followi...
- **component-auditor**: Audit Claude Code agents, skills, commands, and hooks for quality, completeness,...
- **devloop**: Comprehensive helper for working with the DevLoop development observability tool...
- **emoji-remover**: Remove emojis from project files and replace them with text equivalents. Use thi...
- **git-bisect-guide**: Guide automated git bisect sessions to find regression commits with smart test e...
- **git-branch-cleanup**: Automatically clean up merged branches, stale remotes, and organize repository s...
- **parallel-test-bench**: Infrastructure for running parallel agent tests with automatic metric collection...
- **rust-multi-agent**: Coordinated multi-agent workflow for comprehensive Rust development with paralle...
- **rust-test-fix**: Automated Rust testing workflow that runs tests, analyzes failures using pattern...
- **security-infrastructure**: Comprehensive security infrastructure patterns including zero-trust architecture...
- **tech-debt-analyzer**: Identify, quantify, and prioritize technical debt in software projects with acti...
- **test-automation**: Comprehensive test automation patterns including test suite architecture, unit/i...
- **writing-solid-rust**: Apply SOLID principles and hexagonal architecture to Rust code. Teaches trait-ba...

### Minibox

- **minibox:architecture**: Navigate and understand minibox codebase architecture
- **minibox:build-test**: Build, test, and debug workflows for minibox container runtime
- **minibox:runtime**: Run and debug containers with minibox runtime operations
- **minibox:setup**: Development environment setup for minibox container runtime


---

## Alphabetical Index

### ai-slop-remover

Remove AI-generated code slop by comparing current branch against base branch and eliminating unnece...

**Tools:** `Read`, `Edit`, `Bash`, `Grep`, `Glob`


### baml-standards

Expert BAML (BoundaryML) schema design, code review, and test generation following established stand...


### component-auditor

Audit Claude Code agents, skills, commands, and hooks for quality, completeness, and adherence to te...

**Tools:** `Read`, `Grep`, `Glob`, `Bash`


### devloop

Comprehensive helper for working with the DevLoop development observability tool - both using it to ...

**Tools:** `Read`, `Bash`, `Grep`, `Glob`

**Related Skills:** `baml`, `writing-solid-rust`


### emoji-remover

Remove emojis from project files and replace them with text equivalents. Use this skill when the use...


### git-bisect-guide

Guide automated git bisect sessions to find regression commits with smart test execution and commit ...

**Tools:** `Bash`, `Read`


### git-branch-cleanup

Automatically clean up merged branches, stale remotes, and organize repository structure. Use this s...

**Tools:** `Bash`, `Read`


### minibox:architecture

Navigate and understand minibox codebase architecture


### minibox:build-test

Build, test, and debug workflows for minibox container runtime


### minibox:runtime

Run and debug containers with minibox runtime operations


### minibox:setup

Development environment setup for minibox container runtime


### parallel-test-bench

Infrastructure for running parallel agent tests with automatic metric collection, programmatic gradi...


### rust-multi-agent

Coordinated multi-agent workflow for comprehensive Rust development with parallel architecture revie...

**Tools:** `Agent`, `Read`, `Grep`, `Glob`, `Bash`

**Related Skills:** `writing-solid-rust`, `test-automation`


### rust-test-fix

Automated Rust testing workflow that runs tests, analyzes failures using pattern matching, suggests ...

**Tools:** `Read`, `Edit`, `Bash`, `Grep`, `Glob`

**Related Skills:** `tdd:tdd-cycle`, `dev:review-code`, `test-automation`


### security-infrastructure

Comprehensive security infrastructure patterns including zero-trust architecture, compliance automat...

**Tools:** `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`


### tech-debt-analyzer

Identify, quantify, and prioritize technical debt in software projects with actionable remediation p...

**Tools:** `Read`, `Grep`, `Glob`, `Bash`


### test-automation

Comprehensive test automation patterns including test suite architecture, unit/integration/E2E testi...

**Tools:** `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`


### writing-solid-rust

Apply SOLID principles and hexagonal architecture to Rust code. Teaches trait-based ports, domain-dr...

**Tools:** `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`



---

## Skill Dependencies

Shows which skills reference other skills:

### devloop

**Uses:** `baml`, `writing-solid-rust`


### rust-multi-agent

**Uses:** `writing-solid-rust`, `test-automation`


### rust-test-fix

**Uses:** `tdd:tdd-cycle`, `dev:review-code`, `test-automation`


### test-automation

**Used by:** `rust-multi-agent`, `rust-test-fix`


### writing-solid-rust

**Used by:** `devloop`, `rust-multi-agent`



---

## Tool Usage Matrix

Shows which tools are used by each skill:

| Skill | Agent | Bash | Edit | Glob | Grep | Read | Write |
|---|---|---|---|---|---|---|---|
| ai-slop-remover |  | ✓ | ✓ | ✓ | ✓ | ✓ |  |
| baml-standards |  |  |  |  |  |  |  |
| component-auditor |  | ✓ |  | ✓ | ✓ | ✓ |  |
| devloop |  | ✓ |  | ✓ | ✓ | ✓ |  |
| emoji-remover |  |  |  |  |  |  |  |
| git-bisect-guide |  | ✓ |  |  |  | ✓ |  |
| git-branch-cleanup |  | ✓ |  |  |  | ✓ |  |
| minibox:architecture |  |  |  |  |  |  |  |
| minibox:build-test |  |  |  |  |  |  |  |
| minibox:runtime |  |  |  |  |  |  |  |
| minibox:setup |  |  |  |  |  |  |  |
| parallel-test-bench |  |  |  |  |  |  |  |
| rust-multi-agent | ✓ | ✓ |  | ✓ | ✓ | ✓ |  |
| rust-test-fix |  | ✓ | ✓ | ✓ | ✓ | ✓ |  |
| security-infrastructure |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| tech-debt-analyzer |  | ✓ |  | ✓ | ✓ | ✓ |  |
| test-automation |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| writing-solid-rust |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |