---
description: Setup and configure jira-cli for command-line Jira access
allowed-tools: Bash, AskUserQuestion
argument-hint: [--cloud|--server]
---

# Jira CLI Setup

Install and configure `jira-cli` (ankitpokhrel/jira-cli) for command-line Jira access.

## Instructions

### Step 1: Check if jira-cli is installed

```bash
which jira && jira --version
```

### Step 2: Install if needed

**macOS/Linux via Homebrew:**

```bash
brew install jira-cli
```

**Alternative: Binary download:**

```bash
# Check releases at https://github.com/ankitpokhrel/jira-cli/releases
```

### Step 3: Initialize configuration

Run the interactive setup:

```bash
jira init
```

**Setup prompts:**

1. **Installation type**: Cloud or Local (Server/DC)
2. **Jira URL**: e.g., `https://company.atlassian.net`
3. **Authentication**: Email + API token (Cloud) or Bearer token (Server)
4. **Default project**: Optional default project key

### Step 4: Verify setup

```bash
# Test authentication
jira me

# List issues in default project
jira issue list --paginate 5
```

### API Token Generation (for Cloud)

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it (e.g., "jira-cli")
4. Copy and use during `jira init`

### Configuration Location

- Primary: `~/.config/jira-cli/.config.yml`
- Project-specific: `.jira/.config.yml` (in project directory)

### Shell Completion (optional)

```bash
# Bash
echo 'source <(jira completion bash)' >> ~/.bashrc

# Zsh
echo 'source <(jira completion zsh)' >> ~/.zshrc

# Fish
jira completion fish > ~/.config/fish/completions/jira.fish
```
