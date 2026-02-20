# Claude Workspace Development Makefile
# Usage: make <target>

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Directories
AGENTS_DIR := agents
SKILLS_DIR := skills
COMMANDS_DIR := commands
SCRIPTS_DIR := scripts

# Colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

##@ General

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BLUE)Claude Workspace$(RESET)\n\nUsage: make $(GREEN)<target>$(RESET)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Knowledge Graph (run via Claude)

.PHONY: memory-stats
memory-stats: ## Show knowledge graph stats (requires Claude session)
	@echo "Knowledge Graph Statistics"
	@echo "=========================="
	@echo ""
	@echo "Run this command in a Claude session to see memory stats:"
	@echo "  /memory:view"
	@echo ""
	@echo "Or ask Claude: 'show me knowledge graph stats'"

##@ Components

.PHONY: list-agents
list-agents: ## List all agents
	@find $(AGENTS_DIR) -name "*.md" -type f | wc -l | xargs echo "Total agents:"
	@find $(AGENTS_DIR) -type d -mindepth 1 -maxdepth 1 | while read d; do \
		count=$$(find "$$d" -name "*.md" -type f | wc -l | tr -d ' '); \
		echo "  $$(basename $$d): $$count"; \
	done

.PHONY: list-skills
list-skills: ## List all skills
	@find $(SKILLS_DIR) -name "SKILL.md" -type f | wc -l | xargs echo "Total skills:"
	@ls -1 $(SKILLS_DIR)

.PHONY: list-commands
list-commands: ## List all commands
	@find $(COMMANDS_DIR) -name "*.md" -type f | wc -l | xargs echo "Total commands:"
	@find $(COMMANDS_DIR) -type d -mindepth 1 -maxdepth 1 | while read d; do \
		count=$$(find "$$d" -name "*.md" -type f | wc -l | tr -d ' '); \
		echo "  $$(basename $$d): $$count"; \
	done

.PHONY: stats
stats: ## Show workspace statistics
	@echo "$(BLUE)Workspace Statistics$(RESET)"
	@echo "===================="
	@echo "Agents:   $$(find $(AGENTS_DIR) -name '*.md' -type f | wc -l | tr -d ' ')"
	@echo "Skills:   $$(find $(SKILLS_DIR) -name 'SKILL.md' -type f | wc -l | tr -d ' ')"
	@echo "Commands: $$(find $(COMMANDS_DIR) -name '*.md' -type f | wc -l | tr -d ' ')"
	@echo "Scripts:  $$(find $(SCRIPTS_DIR) -type f 2>/dev/null | wc -l | tr -d ' ')"

##@ Validation

.PHONY: validate
validate: validate-agents validate-skills validate-commands ## Validate all components

.PHONY: validate-agents
validate-agents: ## Validate agent frontmatter
	@echo "$(BLUE)Validating agents...$(RESET)"
	@errors=0; \
	for f in $$(find $(AGENTS_DIR) -name "*.md" -type f); do \
		if ! grep -q "^name:" "$$f"; then \
			echo "$(RED)Missing 'name:' in $$f$(RESET)"; \
			errors=$$((errors + 1)); \
		fi; \
		if ! grep -q "^description:" "$$f"; then \
			echo "$(RED)Missing 'description:' in $$f$(RESET)"; \
			errors=$$((errors + 1)); \
		fi; \
	done; \
	if [ $$errors -eq 0 ]; then \
		echo "$(GREEN)All agents valid$(RESET)"; \
	else \
		echo "$(RED)$$errors validation errors$(RESET)"; \
	fi

.PHONY: validate-skills
validate-skills: ## Validate skill structure
	@echo "$(BLUE)Validating skills...$(RESET)"
	@errors=0; \
	for d in $(SKILLS_DIR)/*/; do \
		if [ ! -f "$$d/SKILL.md" ]; then \
			echo "$(RED)Missing SKILL.md in $$d$(RESET)"; \
			errors=$$((errors + 1)); \
		fi; \
	done; \
	if [ $$errors -eq 0 ]; then \
		echo "$(GREEN)All skills valid$(RESET)"; \
	else \
		echo "$(RED)$$errors validation errors$(RESET)"; \
	fi

.PHONY: validate-commands
validate-commands: ## Validate command frontmatter
	@echo "$(BLUE)Validating commands...$(RESET)"
	@errors=0; \
	for f in $$(find $(COMMANDS_DIR) -name "*.md" -type f); do \
		if ! grep -q "^description:" "$$f"; then \
			echo "$(YELLOW)Missing 'description:' in $$f$(RESET)"; \
			errors=$$((errors + 1)); \
		fi; \
	done; \
	if [ $$errors -eq 0 ]; then \
		echo "$(GREEN)All commands valid$(RESET)"; \
	else \
		echo "$(YELLOW)$$errors commands without descriptions$(RESET)"; \
	fi

##@ Code Quality

.PHONY: lint
lint: ## Lint Python files with ruff
	@echo "$(BLUE)Linting Python files...$(RESET)"
	@uv tool run ruff check $(SKILLS_DIR) $(SCRIPTS_DIR) --fix 2>/dev/null || echo "No Python files or ruff not installed"

.PHONY: format
format: ## Format Python files with ruff
	@echo "$(BLUE)Formatting Python files...$(RESET)"
	@uv tool run ruff format $(SKILLS_DIR) $(SCRIPTS_DIR) 2>/dev/null || echo "No Python files or ruff not installed"

.PHONY: check
check: lint validate ## Run all checks

##@ Maintenance

.PHONY: health
health: ## Run health check
	@$(SCRIPTS_DIR)/health-check.sh

.PHONY: cleanup
cleanup: ## Clean up debug files and caches
	@echo "$(BLUE)Cleaning up...$(RESET)"
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(RESET)"

.PHONY: cleanup-debug
cleanup-debug: ## Clean up debug directory
	@$(SCRIPTS_DIR)/cleanup-debug.sh

##@ Conversation Explorer

.PHONY: conv
conv: conversations ## Alias for 'conversations' command

.PHONY: conversations
conversations: ## List recent conversations (limit 10)
	@uv run python scripts/conversation_explorer.py list --limit 10

.PHONY: conv-recent
conv-recent: ## Show conversations from last 3 days
	@uv run python scripts/conversation_explorer.py recent --days 3

.PHONY: conv-today
conv-today: ## Show today's conversations
	@uv run python scripts/conversation_explorer.py recent --days 1

.PHONY: conv-stats
conv-stats: ## Show conversation statistics
	@uv run python scripts/conversation_explorer.py stats

.PHONY: conv-search
conv-search: ## Search conversations (usage: make conv-search QUERY="search term")
	@uv run python scripts/conversation_explorer.py search "$(QUERY)" --limit 5

.PHONY: conv-tools
conv-tools: ## Find conversations using specific tools (usage: make conv-tools TOOL=webfetch)
	@uv run python scripts/conversation_explorer.py tools $(TOOL) | head -20

.PHONY: conv-show
conv-show: ## Show conversation details (usage: make conv-show ID=session_id)
	@uv run python scripts/conversation_explorer.py show $(ID)

.PHONY: conv-long
conv-long: ## Find long conversations (>5 min)
	@uv run python scripts/conversation_explorer.py filter --min-duration 300

.PHONY: conv-active
conv-active: ## Find conversations with many messages (>50)
	@uv run python scripts/conversation_explorer.py filter --min-messages 50

.PHONY: conv-errors
conv-errors: ## Find conversations with tool errors
	@uv run python scripts/conversation_explorer.py filter --errors

.PHONY: conv-export
conv-export: ## Export conversation to JSON (usage: make conv-export ID=session_id)
	@uv run python scripts/conversation_explorer.py export $(ID) --format json

.PHONY: conv-analytics
conv-analytics: ## Show advanced conversation analytics
	@echo "$(BLUE)Running advanced conversation analytics...$(RESET)"
	@uv run python -c "from conversation_explorer.explorer import ConversationExplorer; from conversation_explorer.analytics import ConversationAnalytics; from conversation_explorer.formatter import ConversationFormatter; import json; explorer = ConversationExplorer(); formatter = ConversationFormatter(); convs = explorer.list_conversations(limit=50); full_convs = [explorer.get_conversation(c.session_id) for c in convs[:10] if explorer.get_conversation(c.session_id)]; analytics = ConversationAnalytics(); patterns = analytics.analyze_tool_patterns(full_convs); temporal = analytics.analyze_temporal_patterns(convs); complexity = analytics.analyze_conversation_complexity(full_convs); clusters = analytics.find_conversation_clusters(convs); print('🔍 Tool Usage Patterns:'); [print(f'  {tool}: {rate}% success') for tool, rate in sorted(patterns['success_rates'].items(), key=lambda x: x[1], reverse=True)[:5]]; print('\n📊 Peak Activity:'); print(f'  Peak hour: {temporal[\"peak_hour\"][0]}:00 ({temporal[\"peak_hour\"][1]} conversations)'); print(f'  Peak day: {temporal[\"peak_day\"][0]} ({temporal[\"peak_day\"][1]} conversations)'); print('\n🧠 Complexity Analysis:'); print(f'  Avg tools per conversation: {complexity[\"avg_tools_per_conversation\"]}'); print(f'  Conversations with errors: {complexity[\"conversations_with_errors\"]} ({complexity[\"error_rate\"]}%)'); print(f'  Most complex: {complexity[\"most_complex_conversations\"][0][\"session_id\"][:12]}... ({complexity[\"most_complex_conversations\"][0][\"score\"]} score)' if complexity[\"most_complex_conversations\"] else 'None'); print(f'\n🔗 Conversation clusters: {len(clusters)} groups of related conversations')"

.PHONY: conv-browse
conv-browse: ## Interactive conversation browser
	@echo "$(BLUE)Conversation Explorer - Interactive Mode$(RESET)"
	@echo "================================="
	@echo "$(GREEN)Recent conversations:$(RESET)"
	@make conv-recent
	@echo ""
	@echo "$(YELLOW)Quick commands:$(RESET)"
	@echo "  make conv-show ID=<session>  - View conversation"
	@echo "  make conv-search QUERY=<term> - Search content"
	@echo "  make conv-tools TOOL=<name>   - Find tool usage"
	@echo "  make conv-analytics          - Advanced insights"
	@echo ""
	@echo "Enter command or press Ctrl+C to exit"
	@read -p "Command: " cmd; eval "$$cmd"

.PHONY: conv-help
conv-help: ## Show conversation explorer help
	@echo "$(BLUE)Conversation Explorer Commands$(RESET)"
	@echo "============================="
	@echo "Quick commands:"
	@echo "  $(GREEN)make conversations$(RESET)     - List recent conversations"
	@echo "  $(GREEN)make conv-today$(RESET)        - Show today's conversations"
	@echo "  $(GREEN)make conv-stats$(RESET)        - Show statistics"
	@echo "  $(GREEN)make conv-analytics$(RESET)    - Advanced analytics"
	@echo "  $(GREEN)make conv-browse$(RESET)       - Interactive browser"
	@echo ""
	@echo "Search commands:"
	@echo "  $(GREEN)make conv-search QUERY=\"term\"$(RESET) - Search for text"
	@echo "  $(GREEN)make conv-tools TOOL=webfetch$(RESET)  - Find tool usage"
	@echo "  $(GREEN)make conv-show ID=session$(RESET)     - Show details"
	@echo ""
	@echo "Filter commands:"
	@echo "  $(GREEN)make conv-long$(RESET)         - Long conversations (>5min)"
	@echo "  $(GREEN)make conv-active$(RESET)       - Active conversations (>50 msgs)"
	@echo "  $(GREEN)make conv-errors$(RESET)       - Conversations with errors"
	@echo ""
	@echo "Full CLI help:"
	@echo "  $(GREEN)uv run python scripts/conversation_explorer.py --help$(RESET)"

##@ Search

.PHONY: find-agent
find-agent: ## Find agent by name (usage: make find-agent NAME=foo)
	@grep -rl "name: .*$(NAME)" $(AGENTS_DIR) 2>/dev/null || echo "No agent found matching '$(NAME)'"

.PHONY: find-skill
find-skill: ## Find skill by name (usage: make find-skill NAME=foo)
	@ls -d $(SKILLS_DIR)/*$(NAME)* 2>/dev/null || echo "No skill found matching '$(NAME)'"

.PHONY: grep-all
grep-all: ## Search all components (usage: make grep-all PATTERN=foo)
	@grep -r "$(PATTERN)" $(AGENTS_DIR) $(SKILLS_DIR) $(COMMANDS_DIR) --include="*.md" 2>/dev/null | head -20

##@ Documentation

.PHONY: update-readme
update-readme: ## Auto-generate README from component frontmatter
	@echo "$(BLUE)Generating README...$(RESET)"
	@uv run $(SCRIPTS_DIR)/generate_readme.py
	@echo "$(GREEN)README updated$(RESET)"

.PHONY: check-readme
check-readme: ## Check if README is up-to-date
	@uv run $(SCRIPTS_DIR)/generate_readme.py --check

##@ Development

.PHONY: new-agent
new-agent: ## Create new agent scaffold (usage: make new-agent NAME=foo CATEGORY=testing)
	@mkdir -p $(AGENTS_DIR)/$(CATEGORY)
	@echo "---\nname: $(NAME)\ndescription: \ntools:\n  - Read\n  - Write\n  - Edit\n  - Bash\n---\n\n# $(NAME)\n\n## Purpose\n\n## Instructions\n" > $(AGENTS_DIR)/$(CATEGORY)/$(NAME).md
	@echo "$(GREEN)Created $(AGENTS_DIR)/$(CATEGORY)/$(NAME).md$(RESET)"

.PHONY: new-skill
new-skill: ## Create new skill scaffold (usage: make new-skill NAME=foo)
	@mkdir -p $(SKILLS_DIR)/$(NAME)
	@echo "---\nname: $(NAME)\ndescription: \n---\n\n# $(NAME)\n\n## Overview\n\n## Instructions\n" > $(SKILLS_DIR)/$(NAME)/SKILL.md
	@echo "$(GREEN)Created $(SKILLS_DIR)/$(NAME)/SKILL.md$(RESET)"

.PHONY: new-command
new-command: ## Create new command scaffold (usage: make new-command NAME=foo CATEGORY=dev)
	@mkdir -p $(COMMANDS_DIR)/$(CATEGORY)
	@echo "---\ndescription: \nallowed-tools:\n  - Read\n  - Write\nargument-hint: [arg]\n---\n\n# $(NAME)\n\n## Task\n" > $(COMMANDS_DIR)/$(CATEGORY)/$(NAME).md
	@echo "$(GREEN)Created $(COMMANDS_DIR)/$(CATEGORY)/$(NAME).md$(RESET)"
