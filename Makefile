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
