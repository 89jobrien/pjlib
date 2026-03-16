---
paths: ["**/*.yaml", "**/*.yml"]
---

# YAML Rules

## Formatting

```yaml
# 2-space indentation
key: value
nested:
  child: value
  another: value

# Lists
items:
  - first
  - second
  - third

# Inline lists (when short)
colors: [red, green, blue]

# Multiline strings
description: |
  This is a multiline
  string with preserved
  newlines.

# Folded strings
summary: >
  This is a folded
  string that becomes
  a single line.
```

## Syntax Rules

- **No trailing commas** (invalid in YAML)
- **Consistent indentation** (2 spaces)
- **No tabs** for indentation
- **Quote strings** when they contain special characters

```yaml
# Good
name: "John Doe"
path: "/home/user/file.txt"
version: "1.0"

# Bad
name: John Doe  # May break with special chars
version: 1.0    # Becomes number, not string
```

## Comments

**Use comments sparingly:**

```yaml
# This is a comment
key: value  # Inline comment

# Section: Database Configuration
database:
  host: localhost
  port: 5432
```

**For extensive comments, use `.yamlc` extension** (YAML with Comments)

## Common Structures

### Configuration Files

```yaml
# Application config
app:
  name: myapp
  version: 1.0.0
  debug: false

database:
  host: localhost
  port: 5432
  name: mydb

logging:
  level: INFO
  format: json
```

### CI/CD (GitHub Actions)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: bun test
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./data:/data

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
```

## Anchors and Aliases

**Reuse configuration:**

```yaml
# Define anchor
defaults: &defaults
  timeout: 30
  retries: 3

# Reference alias
production:
  <<: *defaults
  host: prod.example.com

staging:
  <<: *defaults
  host: staging.example.com
```

## Type Coercion

**Be explicit about types:**

```yaml
# Numbers
port: 8080
timeout: 30.5

# Booleans
enabled: true
debug: false

# Strings (quote to avoid coercion)
version: "1.0"      # String, not float
code: "0123"        # String, not octal
answer: "yes"       # String, not boolean

# Null
value: null
empty: ~            # Also null
```

## Best Practices

### DO

- Use consistent indentation (2 spaces)
- Quote strings with special characters
- Use meaningful key names
- Group related configuration
- Add comments for complex sections

### DON'T

- Mix tabs and spaces
- Use trailing commas
- Deeply nest more than 4-5 levels
- Use cryptic abbreviations
- Leave unused keys

## Validation

**Validate YAML before committing:**

```bash
# Check syntax
uv run python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Or use yamllint
brew install yamllint
yamllint config.yaml
```

## Common Files

- `.github/workflows/*.yml` - GitHub Actions
- `docker-compose.yml` - Docker Compose
- `.pre-commit-config.yaml` - Pre-commit hooks
- `config.yaml` - Application configuration
- `openapi.yaml` - API specifications
