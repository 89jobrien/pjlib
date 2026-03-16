---
paths: "**/*.json"
---

# JSON Rules

## Formatting

**Standard formatting:**

```json
{
  "name": "myapp",
  "version": "1.0.0",
  "description": "Application description",
  "nested": {
    "key": "value",
    "array": [1, 2, 3]
  }
}
```

- **2-space indentation**
- **Double quotes** for strings (single quotes invalid)
- **No trailing commas** (invalid JSON)
- **No comments** (use `.jsonc` for JSON with comments)

## Valid Types

```json
{
  "string": "text",
  "number": 42,
  "float": 3.14,
  "boolean": true,
  "null": null,
  "array": [1, 2, 3],
  "object": {
    "nested": "value"
  }
}
```

## Common Files

### package.json (Bun/TypeScript)

```json
{
  "name": "myapp",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "bun --watch src/index.ts",
    "build": "bun build src/index.ts --outdir=dist",
    "test": "bun test"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "types": ["bun-types"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

### .prettierrc

```json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
```

### .vscode/settings.json

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "typescript.tsdk": "node_modules/typescript/lib",
  "files.exclude": {
    "**/.git": true,
    "**/node_modules": true,
    "**/__pycache__": true
  }
}
```

## JSONC (JSON with Comments)

**Use `.jsonc` extension for commented JSON:**

```jsonc
{
  // This is a comment
  "name": "myapp",
  "version": "1.0.0",
  /* Multi-line
     comment */
  "scripts": {
    "dev": "bun dev"
  }
}
```

**Common JSONC files:**

- `tsconfig.json` (TypeScript allows comments)
- `.vscode/*.json` (VS Code allows comments)
- `.markdownlint.json`

## Validation

**Check JSON syntax:**

```bash
# Python
uv run python -c "import json; json.load(open('file.json'))"

# Node/Bun
bun -e "require('./file.json')"

# jq (JSON processor)
jq . file.json
```

## Best Practices

### DO

- Use consistent indentation (2 spaces)
- Quote all string keys and values
- Keep files under 1000 lines (use multiple files)
- Use meaningful key names
- Validate before committing

### DON'T

- Add trailing commas (invalid JSON)
- Use single quotes (invalid JSON)
- Add comments (use .jsonc instead)
- Manually edit large JSON files (use tools)
- Hardcode secrets in JSON files

## Formatting Tools

**Auto-format JSON:**

```bash
# Using prettier
bunx prettier --write file.json

# Using jq
jq . file.json > formatted.json

# Using Python
uv run python -m json.tool file.json
```

## Schema Validation

**JSON Schema for validation:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    }
  },
  "required": ["name", "version"]
}
```
