# Claude Workspace Index

## Stats & health

make stats              # Component counts
make health             # Full health check
make validate           # Validate all components

## Code quality

make lint               # Lint Python with ruff
make format             # Format Python with ruff

## Search

make find-agent NAME=database
make grep-all PATTERN=performance

## Create new components

make new-agent NAME=my-agent CATEGORY=testing
make new-skill NAME=my-skill
make new-command NAME=my-cmd CATEGORY=dev

## Maintenance

make cleanup            # Remove caches
make cleanup-debug      # Clean debug dir

---

## Scripts

### Validate all components

~/.claude/scripts/validate-components.sh

### Search components

~/.claude/scripts/search-components.sh "database"
~/.claude/scripts/search-components.sh "test" agents

---

Comprehensive index of all agents, commands, and skills.

## Agents

### Core

- **dotti**: Dotfiles and configuration management specialist. Use PROACTIVELY for .bashrc, .zshrc, .vimrc, .gitconfig, .tmux.conf, symlink setups, and dotfiles repository management. | Tools: Read, Write, Edit, Bash, Grep | Skills: tool-presets
- **meta-agent**: Generates complete Claude Code sub-agent configuration files from user descriptions with proper frontmatter and syste... | Tools: Read, Write, Edit, Grep, Glob, WebFetch, Task, mcp__plugin_meta-joe_fetch__fetch | Skills: -
- **skill-extractor**: Claude Code skill extraction specialist. Use PROACTIVELY when analyzing agents to identify reusable patterns that can... | Tools: Read, Write, Edit, Grep, Glob, Bash | Skills: -
- **valerie**: Task and todo management specialist. Use PROACTIVELY when users mention tasks, todos, project tracking, task completion, or ask what to work on next. | Tools: Read, Write, Edit, Bash, WebFetch | Skills: tool-presets

### Code Quality

- **code-linter**: Code linting, formatting, and static analysis specialist. Use PROACTIVELY for enforcing coding standards across multiple languages. | Tools: All tools | Skills: -
- **code-reviewer**: Comprehensive code review specialist covering 6 focused aspects - architecture & design, code quality, security & dependencies, performance & scalability, testing coverage, and documentation & API design. Use PROACTIVELY after significant code changes. | Tools: Read, Grep, Glob, Bash, mcp__plugin_meta-joe_fetch__fetch | Skills: code-review, tool-presets
- **todo-organizer**: Extract action items from code review reports and organize them into structured TODO checklists. | Tools: Read, Write, Grep | Skills: -
- **triage-expert**: Context gathering and initial problem diagnosis specialist. Use PROACTIVELY when encountering errors, performance issues, or unexpected behavior. | Tools: Read, Grep, Glob, Bash, Edit | Skills: debugging

### Ai Specialists

- **ai-ethics-advisor**: AI ethics and responsible AI development specialist. Use PROACTIVELY for bias assessment, fairness evaluation, ethica... | Tools: Read, Write, WebSearch, Grep | Skills: -
- **hackathon-ai-strategist**: Expert hackathon strategist and judge. Use PROACTIVELY for AI hackathon ideation, project evaluation, feasibility ass... | Tools: Read, WebSearch, WebFetch | Skills: -
- **llms-maintainer**: LLMs.txt roadmap file generator and maintainer. Use PROACTIVELY after build completion, content changes, or when impl... | Tools: Read, Write, Bash, Grep, Glob | Skills: -
- **model-evaluator**: AI model evaluation and benchmarking specialist. Use PROACTIVELY for model selection, performance comparison, cost an... | Tools: Read, Write, Bash, WebSearch | Skills: -
- **prompt-engineer**: Expert prompt optimization for LLMs and AI systems. Use PROACTIVELY when building AI features, improving agent perfor... | Tools: Read, Write, Edit | Skills: prompt-optimization
- **search-specialist**: Expert web researcher using advanced search techniques and synthesis. Masters search operators, result filtering, and... | Tools: Read, Write, WebSearch, WebFetch | Skills: -
- **task-decomposition-expert**: Complex goal breakdown specialist. Use PROACTIVELY for multi-step projects requiring different capabilities. Masters ... | Tools: Read, Write, Task, TodoWrite | Skills: -

### Data Ai

- **ai-engineer**: LLM application and RAG system specialist. Use PROACTIVELY for LLM integrations, RAG systems, prompt pipelines, vecto... | Tools: Read, Write, Edit, Bash | Skills: prompt-optimization
- **computer-vision-engineer**: Computer vision and image processing specialist. Use PROACTIVELY for image analysis, object detection, face recogniti... | Tools: Read, Write, Edit, Bash | Skills: -
- **data-engineer**: Data pipeline and analytics infrastructure specialist. Use PROACTIVELY for ETL/ELT pipelines, data warehouses, stream... | Tools: Read, Write, Edit, Bash | Skills: -
- **data-scientist**: Data analysis and statistical modeling specialist. Use PROACTIVELY for exploratory data analysis, statistical modelin... | Tools: Read, Write, Edit, Bash | Skills: -
- **ml-engineer**: ML production systems and model deployment specialist. Use PROACTIVELY for ML pipelines, model serving, feature engin... | Tools: Read, Write, Edit, Bash | Skills: -
- **mlops-engineer**: ML infrastructure and operations specialist. Use PROACTIVELY for ML pipelines, experiment tracking, model registries,... | Tools: Read, Write, Edit, Bash | Skills: developer-experience
- **nlp-engineer**: Natural Language Processing and text analytics specialist. Use PROACTIVELY for text processing, language models, sent... | Tools: Read, Write, Edit, Bash | Skills: -
- **quant-analyst**: Quantitative finance and algorithmic trading specialist. Use PROACTIVELY for financial modeling, trading strategy dev... | Tools: Read, Write, Edit, Bash | Skills: -

### Database

- **database-admin**: Database administration specialist for operations, backups, replication, and monitoring. Use PROACTIVELY for database... | Tools: Read, Write, Edit, Bash | Skills: database-optimization
- **database-architect**: Database architecture and design specialist. Use PROACTIVELY for database design decisions, data modeling, scalabilit... | Tools: Read, Write, Edit, Bash | Skills: database-optimization
- **database-optimizer**: Database performance optimization, query tuning, and schema design specialist. Use PROACTIVELY for slow queries, N+1 problems, indexing strategies, execution plan analysis, migration strategies, and caching solutions. | Tools: Read, Write, Edit, Bash | Skills: database-optimization, tool-presets

### Deep Research Team

- **academic-researcher**: Academic research specialist for scholarly sources, peer-reviewed papers, and academic literature. Use PROACTIVELY fo... | Tools: Read, Write, Edit, WebSearch, WebFetch | Skills: lead-research-assistant
- **competitive-intelligence-analyst**: Competitive intelligence and market research specialist. Use PROACTIVELY for competitor analysis, market positioning ... | Tools: Read, Write, Edit, WebSearch, WebFetch | Skills: lead-research-assistant
- **data-analyst**: Quantitative analysis and data-driven research specialist. Use PROACTIVELY for statistical insights, trend analysis, metrics evaluation, data visualization suggestions, and market research. | Tools: Read, Write, Edit, WebSearch, WebFetch | Skills: lead-research-assistant, tool-presets
- **fact-checker**: Fact verification and source validation specialist. Use PROACTIVELY for claim verification, source credibility assess... | Tools: Read, Write, Edit, WebSearch, WebFetch | Skills: lead-research-assistant
- **nia-oracle**: Expert research agent specialized in leveraging Nia's knowledge tools. Use PROACTIVELY for discovering repos/docs, de... | Tools: Read, Grep, Glob, mcp__ide__getDiagnostics, mcp__ide__executeCode, mcp__nia__index, mcp__nia__search_codebase, mcp__nia__regex_search, mcp__nia__search_documentation, mcp__nia__manage_resource, mcp__nia__get_github_file_tree, mcp__nia__nia_web_search, mcp__nia__nia_deep_research_agent, mcp__nia__read_source_content, mcp__nia__nia_package_search_grep, mcp__nia__nia_package_search_hybrid, mcp__nia__nia_package_search_read_file, mcp__nia__nia_bug_report, mcp__nia__context | Skills: lead-research-assistant
- **query-clarifier**: Use this agent when you need to analyze research queries for clarity and determine if user clarification is needed be... | Tools: Read, Write, Edit | Skills: lead-research-assistant
- **report-generator**: Use this agent when you need to transform synthesized research findings into a comprehensive, well-structured final r... | Tools: Read, Write, Edit | Skills: lead-research-assistant, documentation
- **research-brief-generator**: Use this agent when you need to transform a user's research query into a structured, actionable research brief that w... | Tools: Read, Write, Edit | Skills: lead-research-assistant
- **research-coordinator**: Use this agent when you need to strategically plan and coordinate complex research tasks across multiple specialist r... | Tools: Read, Write, Edit, Task, TodoWrite | Skills: lead-research-assistant
- **research-orchestrator**: Use this agent when you need to coordinate a comprehensive research project that requires multiple specialized agents... | Tools: Read, Write, Edit, Task, TodoWrite | Skills: lead-research-assistant
- **research-synthesizer**: Use this agent when you need to consolidate and synthesize findings from multiple research sources or specialist rese... | Tools: Read, Write, Edit | Skills: lead-research-assistant
- **technical-researcher**: Use this agent when you need to analyze code repositories, technical documentation, implementation details, or evalua... | Tools: Read, Write, Edit, WebSearch, WebFetch, Bash | Skills: lead-research-assistant

### Development Team

- **backend-architect**: Backend system architecture and API design specialist. Use PROACTIVELY for RESTful APIs, microservice boundaries, dat... | Tools: Read, Write, Edit, Bash | Skills: documentation, database-optimization
- **cli-ui-designer**: CLI interface design specialist. Use PROACTIVELY to create terminal-inspired user interfaces with modern web technolo... | Tools: Read, Write, Edit, MultiEdit, Glob, Grep | Skills: command-optimization
- **devops-engineer**: DevOps and infrastructure specialist for CI/CD, deployment automation, and cloud operations. Use PROACTIVELY for pipe... | Tools: Read, Write, Edit, Bash | Skills: developer-experience
- **frontend-developer**: Frontend development specialist for React applications and responsive design. Use PROACTIVELY for UI components, stat... | Tools: Read, Write, Edit, Bash | Skills: performance, web-accessibility
- **fullstack-developer**: Full-stack development specialist covering frontend, backend, and database technologies. Use PROACTIVELY for end-to-e... | Tools: Read, Write, Edit, Bash | Skills: performance, documentation, database-optimization
- **ui-ux-designer**: UI/UX design specialist for user-centered design and interface systems. Use PROACTIVELY for user research, wireframes... | Tools: Read, Write, Edit | Skills: web-accessibility

### Development Tools

- **command-expert**: CLI command development specialist for the claude-code-templates system. Use PROACTIVELY for command design, argument... | Tools: Read, Write, Edit | Skills: command-optimization
- **context-manager**: Context management specialist for multi-agent workflows and long-running tasks. Use PROACTIVELY for complex projects,... | Tools: Read, Write, Edit, TodoWrite | Skills: context-management
- **debugger**: Debugging specialist for errors, test failures, and unexpected behavior. Use PROACTIVELY when encountering issues, an... | Tools: Read, Write, Edit, Bash, Grep, mcp__ide__getDiagnostics, mcp__ide__executeCode | Skills: debugging
- **dx-optimizer**: Developer Experience specialist for tooling, setup, and workflow optimization. Use PROACTIVELY when setting up projec... | Tools: Read, Write, Edit, Bash | Skills: developer-experience
- **error-detective**: Log analysis and error pattern detection specialist. Use PROACTIVELY for debugging issues, analyzing logs, investigat... | Tools: Read, Write, Edit, Bash, Grep | Skills: debugging
- **mcp-expert**: Model Context Protocol (MCP) integration specialist for the cli-tool components system. Use PROACTIVELY for MCP serve... | Tools: Read, Write, Edit | Skills: mcp-integration
- **unused-code-cleaner**: Detects and removes unused code (imports, functions, classes) across multiple languages. Use PROACTIVELY after refact... | Tools: Read, Write, Edit, Bash, Grep, Glob | Skills: dead-code-removal, testing

### Devops Infrastructure

- **cloud-architect**: Cloud infrastructure design and optimization specialist for AWS/Azure/GCP. Use PROACTIVELY for infrastructure archite... | Tools: Read, Write, Edit, Bash | Skills: -
- **deployment-engineer**: CI/CD and deployment automation specialist. Use PROACTIVELY for pipeline configuration, Docker containers, Kubernetes... | Tools: Read, Write, Edit, Bash, AskUserQuestion | Skills: developer-experience
- **devops-troubleshooter**: Production troubleshooting and incident response specialist. Use PROACTIVELY for debugging issues, log analysis, depl... | Tools: Read, Write, Edit, Bash, Grep | Skills: debugging
- **monitoring-specialist**: Monitoring and observability infrastructure specialist. Use PROACTIVELY for metrics collection, alerting systems, log... | Tools: Read, Write, Edit, Bash | Skills: performance
- **network-engineer**: Network connectivity and infrastructure specialist. Use PROACTIVELY for debugging network issues, load balancer confi... | Tools: Read, Write, Edit, Bash | Skills: -
- **security-engineer**: Security infrastructure and compliance specialist. Use PROACTIVELY for security architecture, compliance frameworks, ... | Tools: Read, Write, Edit, Bash | Skills: -

### Documentation

- **api-documenter**: Create OpenAPI/Swagger specs, generate SDKs, and write developer documentation. Handles versioning, examples, and int... | Tools: Read, Write, Edit, Bash | Skills: documentation
- **changelog-generator**: Changelog and release notes specialist. Use PROACTIVELY for generating changelogs from git history, creating release ... | Tools: Read, Write, Edit, Bash | Skills: documentation
- **technical-writer**: Technical writing and content creation specialist. Use PROACTIVELY for user guides, tutorials, README files, architec... | Tools: Read, Write, Edit, Grep | Skills: documentation

### Expert Advisors

- **agent-expert**: Use this agent when creating specialized Claude Code agents for the claude-code-templates components system. Specializes in agent design, prompt engineering, domain expertise modeling, and agent best practices. | Tools: Read, Write, Edit, Grep | Skills: -
- **architect-reviewer**: Use this agent to review code for architectural consistency and patterns. Specializes in SOLID principles, proper lay... | Tools: Read, Write, Edit, Grep | Skills: code-review
- **dependency-manager**: Use this agent to manage project dependencies. Specializes in dependency analysis, vulnerability scanning, and licens... | Tools: - | Skills: dependency-management
- **documentation-expert**: Use this agent to create, improve, and maintain project documentation. Specializes in technical writing, documentatio... | Tools: Read, Write, Edit, Grep | Skills: documentation
- **pytest-tdd-expert**: Python/pytest TDD specialist for auditing test quality, running tests with coverage, and generating comprehensive tes... | Tools: Read, Write, Edit, Bash, Grep, Glob | Skills: testing, tdd-pytest
- **skill-creator-expert**: Skill creation specialist. Use PROACTIVELY when users want to create new skills, update existing skills, or need guid... | Tools: Read, Write, Edit, Bash, Grep, Glob | Skills: skill-creator

### Performance Testing

- **load-testing-specialist**: Load testing and stress testing specialist. Use PROACTIVELY for creating comprehensive load test scenarios, analyzing... | Tools: Read, Write, Edit, Bash | Skills: performance
- **performance-engineer**: Profile applications, optimize bottlenecks, and implement caching strategies. Handles load testing, CDN setup, and qu... | Tools: Read, Write, Edit, Bash | Skills: performance
- **react-performance-optimization**: React performance optimization specialist. Use PROACTIVELY for identifying and fixing performance bottlenecks, bundle... | Tools: Read, Write, Edit, Bash | Skills: performance
- **web-vitals-optimizer**: Core Web Vitals optimization specialist. Use PROACTIVELY for improving LCP, FID, CLS, and other web performance metri... | Tools: Read, Write, Edit, Bash | Skills: performance, seo-analysis

### Testing

- **cli-expert**: CLI tool development and npm package specialist. Use PROACTIVELY for building CLI tools, argument parsing, and Unix-style commands. | Tools: All tools | Skills: -
- **integration-tester**: Tests agents and frontend integration after refactoring. Use PROACTIVELY to validate system integration. | Tools: Bash, Read, Grep, Glob | Skills: testing
- **logging-specialist**: Log analysis and logging infrastructure specialist. Use PROACTIVELY for log debugging, structured logging, and security auditing. | Tools: Read, Grep, Glob, Edit, Write, Bash | Skills: debugging
- **parallel-tdd-expert**: Parallelized TDD implementation specialist. Use PROACTIVELY for implementing multiagent features using strict TDD workflow. | Tools: Read, Write, Edit, Bash, Grep, Glob | Skills: testing, tdd-pytest
- **performance-profiler**: Performance analysis and optimization specialist. Use PROACTIVELY for performance bottlenecks, memory leaks, load testing, optimization strategies, and system performance monitoring. | Tools: Read, Write, Edit, Bash | Skills: performance, tool-presets
- **test-automator**: Create comprehensive test suites with unit, integration, and e2e tests. Sets up CI pipelines, mocking strategies, and test data. Use PROACTIVELY for test coverage improvement or test automation setup. | Tools: Read, Write, Edit, Bash | Skills: testing, tool-presets
- **test-engineer**: Test automation and quality assurance specialist. Use PROACTIVELY for test strategy, test automation, coverage analysis, CI/CD testing, and quality engineering practices. | Tools: Read, Write, Edit, Bash | Skills: testing, tool-presets

### Programming Languages

- **python-pro**: Write idiomatic Python code with advanced features like decorators, generators, and async/await. Optimizes performanc... | Tools: Read, Write, Edit, Bash | Skills: tdd-pytest, testing
- **rust-pro**: Write idiomatic Rust with ownership patterns, lifetimes, and trait implementations. Masters async/await, safe concurr... | Tools: Read, Write, Edit, Bash | Skills: testing
- **shell-scripting-pro**: Write robust shell scripts with proper error handling, POSIX compliance, and automation patterns. Masters bash/zsh fe... | Tools: Read, Write, Edit, Bash | Skills: -
- **sql-pro**: Write complex SQL queries, optimize execution plans, and design normalized schemas. Masters CTEs, window functions, a... | Tools: Read, Write, Edit, Bash | Skills: database-optimization
- **typescript-pro**: Write idiomatic TypeScript with advanced type system features, strict typing, and modern patterns. Masters generic co... | Tools: Read, Write, Edit, Bash | Skills: testing

### Memory

- **memory-manager**: Specialist for managing persistent memory using the knowledge graph. Use for storing entities, creating relationships, adding observations, searching stored knowledge, and maintaining context across conversations. | Tools: Read, Write, Edit, Grep, Glob, mcp__memory__* | Skills: -

### Utilitarian

- **slop-remover**: Remove AI-generated code slop from branches. Use PROACTIVELY after AI-assisted coding sessions to clean up defensive ... | Tools: Read, Edit, MultiEdit, Bash, Grep, Glob | Skills: ai-code-cleanup

### Web Tools

- **nextjs-architecture-expert**: Master of Next.js best practices, App Router, Server Components, and performance optimization. Use PROACTIVELY for Ne... | Tools: Read, Write, Edit, Bash, Grep, Glob | Skills: nextjs-architecture
- **react-performance-optimizer**: Specialist in React performance patterns, bundle optimization, and Core Web Vitals. Use PROACTIVELY for React app per... | Tools: Read, Write, Edit, Bash, Grep | Skills: performance
- **seo-analyzer**: SEO analysis and optimization specialist. Use PROACTIVELY for technical SEO audits, meta tag optimization, performanc... | Tools: Read, Write, WebFetch, Grep, Glob | Skills: seo-analysis
- **url-context-validator**: URL validation and contextual analysis specialist. Use PROACTIVELY for validating links not just for functionality bu... | Tools: Read, Write, WebFetch, WebSearch | Skills: url-analysis
- **url-link-extractor**: URL and link extraction specialist. Use PROACTIVELY for finding, extracting, and cataloging all URLs and links within... | Tools: Read, Write, Grep, Glob, LS | Skills: url-analysis
- **web-accessibility-checker**: Web accessibility compliance specialist. Use PROACTIVELY for WCAG compliance audits, accessibility testing, screen re... | Tools: Read, Write, Grep, Glob | Skills: web-accessibility

## Commands

### Root Commands

- **analyze-codebase**: Run parallel code review, test audit, and architecture analysis
- **branch-cleanup**: Use PROACTIVELY to clean up merged branches, stale remotes, and organize branch structure
- **code-to-task**: Convert code changes to task descriptions
- **create-prd**: Create Product Requirements Document (PRD) for new features
- **create-pull-request**: Create a new branch, commit changes, and submit a pull request
- **create-skill**: Create a new Claude Skill following best practices. Guides through the complete skill creation process from concept t...

### Context

- **do-deep-dive**: Analyze directory structure, architecture and implementation principles
- **list-claude-tools**: Shortcut to see all available Claude tools
- **prime**: Load context for a new agent session by analyzing codebase structure, documentation and README

### Dev

- **containerize-application**: Containerize application with optimized Docker configuration, security, and multi-stage builds
- **debug-error**: Systematically debug and fix errors with comprehensive methodology
- **design-rest-api**: Design RESTful API architecture with comprehensive endpoints, authentication, and documentation
- **remove-ai-slop**: Remove AI-generated code slop from the current branch by comparing against a base branch
- **review-architecture**: Comprehensive architecture review with design patterns analysis and improvement recommendations
- **review-code**: Comprehensive code quality review with security, performance, and architecture analysis

### Docs

- **create-architecture-documentation**: Generate comprehensive architecture documentation with diagrams, ADRs, and interactive visualization
- **create-onboarding-guide**: Create comprehensive developer onboarding guide with environment setup, workflows, and interactive tutorials
- **update-docs**: Systematically update project documentation with implementation status, API changes, and synchronized content

### Git

- **clean-branches**: Clean up merged and stale git branches
- **create-pr**: Create a new branch, commit changes, and submit a pull request
- **create-worktrees**: Create git worktrees for all open PRs
- **fix-github-issue**: Analyze and fix a GitHub issue by implementing necessary changes
- **git-bisect-helper**: Use PROACTIVELY to guide automated git bisect sessions for finding regression commits with smart test execution
- **git-status**: Show detailed git repository status with differences from remote
- **pr-review**: Conduct thorough code review on a pull request with multiple perspectives
- **update-branch-name**: Update current branch name based on changes analysis

### Memory

- **add**: Add new entities or observations to the knowledge graph
- **forget**: Remove entities, relationships, or observations from the knowledge graph
- **relate**: Create relationships between entities in the knowledge graph
- **search**: Search and query the knowledge graph for stored information
- **view**: View the knowledge graph or specific entities with their relationships

### Meta

- **create-command**: Create a new Claude Code slash command with full feature support
- **create-subagent**: Create a specialized AI subagent following domain expert principles

### Setup

- **design-database-schema**: Design optimized database schemas with proper relationships, constraints, and performance considerations
- **implement-graphql-api**: Implement GraphQL API with comprehensive schema, resolvers, and real-time subscriptions
- **setup-ci-cd-pipeline**: Setup comprehensive CI/CD pipeline with automated testing, deployment, and monitoring
- **setup-development-environment**: Setup comprehensive development environment with tools, configurations, and workflows
- **setup-docker-containers**: Setup Docker containerization with multi-stage builds and development workflows
- **setup-formatting**: Configure comprehensive code formatting tools with consistent style enforcement
- **setup-linting**: Configure comprehensive code linting and quality analysis tools with automated enforcement
- **setup-monitoring-observability**: Setup comprehensive monitoring and observability with metrics, logging, tracing, and alerting
- **setup-monorepo**: Configure monorepo project structure with comprehensive workspace management and build orchestration
- **setup-rate-limiting**: Implement comprehensive API rate limiting with advanced algorithms and user-specific policies

### Test

- **init**: Initialize test configuration by detecting framework (pytest, Jest, Vitest, etc.) and setting up test directory struc...
- **report**: Generate or update TESTING_REPORT.local.md with comprehensive test audit, coverage analysis, and recommendations. Fra...
- **run**: Run tests with framework detection. Supports pytest, Jest, Vitest, and other common test frameworks. Shows pass/fail ...
- **test**: Write tests using TDD methodology. Context-aware analysis of conversation history to determine what to test, or accep...

### Todo

- **add**: Add a new todo to TO-DO.md. If no task description is provided, uses conversation history as context. Optionally acce...
- **complete**: Mark todo N as completed and move it from Active to Completed section in TO-DO.md.
- **due**: Set or update the due date for todo N in TO-DO.md.
- **list**: List todos from TO-DO.md. Show all todos, N todos, next task, or past due tasks.
- **remove**: Remove todo N entirely from TO-DO.md (from either Active or Completed section).
- **undo**: Mark completed todo N as incomplete and move it back to Active section in TO-DO.md.

### Util

- **check-file**: Perform comprehensive analysis of a file for code quality, security, and optimization
- **clean**: Fix all black, isort, flake8 and mypy issues in the entire codebase
- **code-permutation-tester**: Test multiple code variations through simulation before implementation
- **create-database-migrations**: Create and manage database migrations with proper versioning and rollback support
- **explain-code**: Analyze and explain code functionality with comprehensive breakdown
- **ultra-think**: Deep analysis and problem solving with multi-dimensional thinking
- **update-dependencies**: Update and modernize project dependencies with comprehensive testing and compatibility checks

## Skills

- **ai-code-cleanup**: Remove AI-generated code slop from branches. Use after AI-assisted coding sessions to clean up defensive bloat, unnec... | Used by: slop-remover
- **ai-ethics**: Responsible AI development specialist for bias detection, fairness evaluation, and ethical AI implementation. | Used by: ai-ethics-advisor
- **cloud-infrastructure**: Cloud infrastructure patterns for AWS/Azure/GCP including IaC, cost optimization, and multi-cloud strategies. | Used by: cloud-architect, security-engineer, network-engineer
- **devops-runbooks**: Operational runbook and procedure documentation for incident response and system maintenance. | Used by: devops-troubleshooter, deployment-engineer
- **git-commit-helper**: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages ... | Used by: -
- **git-workflow**: Git workflow and pull request patterns for branching strategies, code review, and git conventions. | Used by: git-expert
- **machine-learning**: ML lifecycle patterns for model training, evaluation, deployment, and monitoring. | Used by: ml-engineer, data-scientist, data-engineer, computer-vision-engineer, nlp-engineer, quant-analyst
- **network-engineering**: Network design patterns for DNS, SSL/TLS, load balancing, and connectivity troubleshooting. | Used by: network-engineer
- **pdf-processing**: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user... | Used by: -
- **python-scripting**: Python scripting patterns with uv and PEP 723 inline dependencies for standalone scripts. | Used by: python-pro
- **security-audit**: Security auditing for vulnerability assessment, OWASP Top 10, and remediation planning. | Used by: security-engineer, code-reviewer
- **security-engineering**: Security architecture patterns for authentication, authorization, encryption, and compliance. | Used by: cloud-architect, security-engineer
- **shell-scripting**: Bash/zsh scripting patterns for automation, error handling, and POSIX compliance. | Used by: shell-scripting-pro
- **technical-research**: Technical research methodology for code analysis, documentation review, and implementation evaluation. | Used by: technical-researcher
- **cocoindex**: Comprehensive toolkit for developing with the CocoIndex library. Use when users need to create data transformation pi... | Used by: - | References: api_operations.md, cli_operations.md, custom_functions.md, flow_patterns.md
- **code-review**: Expert code review specialist for quality, security, and maintainability. Use when reviewing code changes, ensuring h... | Used by: code-reviewer, architect-reviewer | References: review_checklist.md
- **command-optimization**: CLI command development specialist. Use when creating commands, designing argument parsing, automating tasks, or impl... | Used by: cli-ui-designer, command-expert
- **context-management**: Context management specialist for multi-agent workflows and long-running tasks. Use when coordinating multiple agents... | Used by: context-manager
- **database-optimization**: SQL query optimization and database performance specialist. Use when optimizing slow queries, fixing N+1 problems, de... | Used by: database-admin, database-architect, database-optimization, database-optimizer, backend-architect, fullstack-developer, sql-pro
- **dead-code-removal**: Detects and safely removes unused code (imports, functions, classes) across multiple languages. Use after refactoring... | Used by: unused-code-cleaner | Scripts: find_unused_imports.py
- **debugging**: Comprehensive debugging specialist for errors, test failures, log analysis, and system problems. Use when encounterin... | Used by: debugger, error-detective, devops-troubleshooter | References: debugging_workflows.md | Scripts: parse_logs.py
- **dependency-management**: Dependency management specialist. Use when updating dependencies, scanning for vulnerabilities, analyzing dependency ... | Used by: dependency-manager | References: package_managers.md | Scripts: parse_dependencies.py
- **developer-experience**: Developer Experience specialist for tooling, setup, and workflow optimization. Use when setting up projects, reducing... | Used by: mlops-engineer, devops-engineer, dx-optimizer, deployment-engineer
- **developer-growth-analysis**: Analyzes your recent Claude Code chat history to identify coding patterns, development gaps, and areas for improvemen... | Used by: -
- **documentation**: Comprehensive documentation specialist covering API documentation, technical writing, and changelog generation. Use w... | Used by: report-generator, backend-architect, fullstack-developer, api-documenter, changelog-generator, technical-writer, documentation-expert | References: api_docs.md, changelogs.md, technical_writing.md
- **file-converter**: This skill handles file format conversions across documents (PDF, DOCX, Markdown, HTML, TXT), data files (JSON, CSV, ... | Used by: - | References: data-conversions.md, document-conversions.md, image-conversions.md
- **file-organizer**: Intelligently organizes your files and folders across your computer by understanding context, finding duplicates, sug... | Used by: -
- **lead-research-assistant**: Identifies high-quality leads for your product or service by analyzing your business, searching for target companies,... | Used by: academic-researcher, competitive-intelligence-analyst, data-analyst, fact-checker, nia-oracle, query-clarifier, report-generator, research-brief-generator, research-coordinator, research-orchestrator, research-synthesizer, technical-researcher
- **mcp-integration**: Model Context Protocol (MCP) integration specialist. Use when creating MCP server configurations, implementing MCP in... | Used by: mcp-expert
- **meeting-insights-analyzer**: Analyzes meeting transcripts and recordings to uncover behavioral patterns, communication insights, and actionable fe... | Used by: -
- **nextjs-architecture**: Next.js architecture specialist. Use when designing Next.js applications, migrating to App Router, implementing Serve... | Used by: nextjs-architecture-expert
- **performance**: Comprehensive performance specialist covering analysis, optimization, load testing, and framework-specific performanc... | Used by: frontend-developer, fullstack-developer, performance-profiler, monitoring-specialist, load-testing-specialist, performance-engineer, react-performance-optimization, web-vitals-optimizer, react-performance-optimizer | References: framework_patterns.md, load_testing.md, react_patterns.md
- **global-standards**: Project-wide coding standards and conventions specialist. Use PROACTIVELY when writing code, making architectural dec... | Used by: - | References: coding-style.md, commenting.md, conventions.md, error-handling.md, tech-stack.md, validation.md
- **prompt-optimization**: Expert prompt optimization for LLMs and AI systems. Use when building AI features, improving agent performance, craft... | Used by: prompt-engineer, ai-engineer
- **seo-analysis**: SEO analysis and optimization specialist. Use when conducting technical SEO audits, optimizing meta tags, analyzing C... | Used by: web-vitals-optimizer, seo-analyzer
- **skill-creator**: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an ex... | Used by: skill-creator-expert | Scripts: init_skill.py, package_skill.py, quick_validate.py
- **skill-share**: A skill that creates new Claude skills and automatically shares them on Slack using Rube for seamless team collaborat... | Used by: -
- **tdd-pytest**: Python/pytest TDD specialist for test-driven development workflows. Use when writing tests, auditing test quality, ru... | Used by: pytest-tdd-expert, python-pro
- **testing**: Comprehensive testing specialist covering test strategy, automation, TDD methodology, test writing, and web app testi... | Used by: test-engineer, unused-code-cleaner, pytest-tdd-expert, test-automator, python-pro, rust-pro, typescript-pro | References: framework_workflows.md, test_patterns.md, webapp_testing.md | Scripts: with_server.py
- **tool-presets**: Standardized tool set definitions for agents. Provides reusable presets (dev-tools, file-ops, analysis, research, orchestration) for consistent tool access. | Used by: dotti, valerie, data-analyst, test-automator, performance-profiler, test-engineer, database-optimizer, code-reviewer | References: dev-tools.md, file-ops.md, analysis.md, research.md, orchestration.md
- **url-analysis**: URL validation and contextual analysis specialist. Use when validating links, analyzing URL context, extracting links... | Used by: url-context-validator, url-link-extractor | Scripts: validate_urls.py
- **web-accessibility**: Web accessibility compliance specialist. Use when conducting WCAG compliance audits, testing screen reader compatibil... | Used by: frontend-developer, ui-ux-designer, web-accessibility-checker
